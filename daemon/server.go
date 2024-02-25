package server

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strconv"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"github.com/chaitanyabsprip/cartographer/cartographer"
	"github.com/chaitanyabsprip/cartographer/config"
)

func initialise(init chan bool) {
	config := config.Config
	fmt.Println(os.Getwd())
	log.Println("initialising python daemon")

	cmd := exec.Command(config.PythonInterpreter, "cartographer/cli.py", "-D")
	cmd.Stdout = log.Writer()
	cmd.Stderr = log.Writer()
	cmd.Start()

	// implement a way to block until the server is actually ready
	// maybe keep hitting /info endpoint in infinite loop with a timeout
	log.Println("python daemon started")
	init <- true
}

func index(c echo.Context) error {
	filepath := c.QueryParam("filepath")
	cartographer.Index(filepath)
	return c.String(http.StatusOK, fmt.Sprintf("Indexed file %v", filepath))
}

func search(c echo.Context) error {
	query := c.QueryParam("query")
	limit := c.QueryParam("limit")
	lim, err := strconv.Atoi(limit)
	if err != nil {
		lim = -1
	}
	if lim < 1 {
		return echo.NewHTTPError(http.StatusBadRequest, "limit must be a positive integer")
	}
	out, err := cartographer.Search(query, lim)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}
	return c.JSON(http.StatusOK, out)
}

func health(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]string{
		"health": "ok",
	})
}

func info(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]int{
		"pid": os.Getpid(),
	})
}

func Run() {
	initialised := make(chan bool)
	go initialise(initialised)
	<-initialised
	e := echo.New()
	log.Println("Server started")
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Pre(middleware.RemoveTrailingSlash())

	e.GET("/index", index)
	e.GET("/search", search)
	e.GET("/health", health)
	e.GET("/info", info)
	e.Logger.Fatal(e.Start("0.0.0.0:30001"))
}
