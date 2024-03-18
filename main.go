package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	python3 "github.com/sublime-security/cpy3"

	app "github.com/chaitanyabsprip/cartographer/cartographer"
	"github.com/chaitanyabsprip/cartographer/embedding"
	"github.com/chaitanyabsprip/cartographer/utils"
)

var (
	daemonFlag bool
	limit      int
	indexPath  string
	query      string
)

const usage = `
Usage: %[1]s [options] <command>

Options:
  -h, --help                    Show this help message
  -D, --daemon                  Run the application as a daemon

Commands:
  index [filepath]              Index documents

  query [options] <querystring> Query indexed documents
    -l, --limit                 Limit the number of results

Examples:
  %[1]s index /path/to/file/to/index
  %[1]s query -l 10 "What does this do?"
`

func initialise() {
	utils.CreateAppDirs()
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	file := utils.OpenLogFile("debug.log")
	log.SetOutput(file)
	if len(os.Args) < 2 {
		fmt.Println("expected 'index' or 'query' subcommands")
		os.Exit(1)
	}

	binaryName := filepath.Base(os.Args[0])

	flag.Usage = func() {
		fmt.Printf(usage, binaryName)
		os.Exit(1)
	}

	flag.BoolVar(&daemonFlag, "daemon", false, "Run the application as a daemon")
	flag.BoolVar(&daemonFlag, "d", false, "Run the application as a daemon")
	app.Initialise()
	embedding.Initialize(app.Config.TransformerName)
}

func main() {
	defer python3.Py_Finalize()
	initialise()
	indexCmds := flag.NewFlagSet("index", flag.ExitOnError)
	queryCmds := flag.NewFlagSet("query", flag.ExitOnError)
	queryCmds.IntVar(&limit, "limit", 9999, "Limit the number of results")
	queryCmds.IntVar(&limit, "l", 9999, "Limit the number of results")

	switch os.Args[1] {
	case "index":
		indexCmds.Parse(os.Args[2:])
		if len(indexCmds.Args()) > 0 {
			indexPath = indexCmds.Args()[0]
		}
		app.Index(indexPath)
	case "query":
		if len(os.Args) < 3 {
			flag.Usage()
		}
		queryCmds.Parse(os.Args[2:])
		query = queryCmds.Args()[0]
		app.Search(query, limit)

	default:
		flag.Parse()
	}

	if daemonFlag {
		app.Serve()
	}
}
