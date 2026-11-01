// Ayah by Ayah — Windows desktop edition (read & study).
// One exe: the public site is embedded; it starts a private web server on this computer (127.0.0.1 only)
// and opens it in its own window (Microsoft Edge app window, else Chrome, else the default browser).
// Settings (language, font, bookmark) are kept between runs in %LOCALAPPDATA%\AyahByAyah.
package main

import (
	"embed"
	"fmt"
	"io/fs"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync/atomic"
	"time"
)

//go:embed all:site
var siteFS embed.FS

const preferredPort = 47213

var lastPing atomic.Int64 // unix seconds of the last heartbeat from the page
var seenPing atomic.Bool

func main() {
	sub, err := fs.Sub(siteFS, "site")
	if err != nil {
		fatal(err)
	}
	noOpen := len(os.Args) > 1 && os.Args[1] == "--no-open"

	mux := http.NewServeMux()
	fileServer := http.FileServer(http.FS(sub))
	mux.HandleFunc("/__ping", func(w http.ResponseWriter, r *http.Request) {
		lastPing.Store(time.Now().Unix())
		seenPing.Store(true)
		w.Header().Set("Cache-Control", "no-store")
		w.WriteHeader(http.StatusNoContent)
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		p := r.URL.Path
		switch {
		case strings.HasSuffix(p, ".json"):
			w.Header().Set("Content-Type", "application/json; charset=utf-8")
		case strings.HasSuffix(p, ".html") || p == "/":
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
		case strings.HasSuffix(p, ".woff2"):
			w.Header().Set("Content-Type", "font/woff2")
		}
		w.Header().Set("Cache-Control", "no-cache")
		if p == "/" || p == "/index.html" {
			serveIndex(w, sub)
			return
		}
		fileServer.ServeHTTP(w, r)
	})

	ln, err := net.Listen("tcp", fmt.Sprintf("127.0.0.1:%d", preferredPort))
	if err != nil {
		ln, err = net.Listen("tcp", "127.0.0.1:0")
		if err != nil {
			fatal(err)
		}
	}
	port := ln.Addr().(*net.TCPAddr).Port
	url := fmt.Sprintf("http://127.0.0.1:%d/", port)
	go http.Serve(ln, mux)

	if noOpen {
		fmt.Println("serving", url)
	} else {
		openWindow(url)
	}

	// Exit when the window has been closed: the page pings every 5 s; stop after 25 s of silence.
	started := time.Now()
	for {
		time.Sleep(3 * time.Second)
		now := time.Now().Unix()
		if seenPing.Load() {
			if now-lastPing.Load() > 25 {
				return
			}
		} else if time.Since(started) > 90*time.Second {
			return // the window never opened
		}
	}
}

// index.html with a small heartbeat script added, so the program can end itself when the window is closed.
func serveIndex(w http.ResponseWriter, sub fs.FS) {
	b, err := fs.ReadFile(sub, "index.html")
	if err != nil {
		http.Error(w, "index.html missing", 500)
		return
	}
	s := string(b)
	hb := `<script>try{setInterval(function(){fetch("/__ping",{cache:"no-store"}).catch(function(){})},5000);fetch("/__ping",{cache:"no-store"}).catch(function(){})}catch(e){}</script>`
	if i := strings.LastIndex(s, "</body>"); i >= 0 {
		s = s[:i] + hb + s[i:]
	} else {
		s += hb
	}
	w.Write([]byte(s))
}

func dataDir() string {
	base := os.Getenv("LOCALAPPDATA")
	if base == "" {
		base, _ = os.UserCacheDir()
	}
	d := filepath.Join(base, "AyahByAyah", "profile")
	os.MkdirAll(d, 0o755)
	return d
}

func openWindow(url string) {
	if runtime.GOOS == "windows" {
		cands := []string{}
		for _, env := range []string{"ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"} {
			if b := os.Getenv(env); b != "" {
				cands = append(cands,
					filepath.Join(b, "Microsoft", "Edge", "Application", "msedge.exe"),
					filepath.Join(b, "Google", "Chrome", "Application", "chrome.exe"))
			}
		}
		for _, exe := range cands {
			if _, err := os.Stat(exe); err == nil {
				cmd := exec.Command(exe, "--app="+url, "--user-data-dir="+dataDir(), "--no-first-run",
					"--no-default-browser-check", "--window-size=1180,900")
				if cmd.Start() == nil {
					return
				}
			}
		}
		exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
		return
	}
	for _, c := range []string{"xdg-open", "open"} {
		if p, err := exec.LookPath(c); err == nil {
			exec.Command(p, url).Start()
			return
		}
	}
}

func fatal(err error) {
	if runtime.GOOS == "windows" {
		os.WriteFile(filepath.Join(os.TempDir(), "AyahByAyah-error.txt"), []byte(err.Error()), 0o644)
	} else {
		fmt.Fprintln(os.Stderr, err)
	}
	os.Exit(1)
}
