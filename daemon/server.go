package server

import (
	"context"
	"fmt"
	"log"
	"log/slog"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"github.com/chaitanyabsprip/cartographer/cartographer"
	"github.com/chaitanyabsprip/cartographer/config"
	"github.com/chaitanyabsprip/cartographer/utils"
)

func initialise(init chan bool) {
	config := config.Config
	log.Println("initialising python daemon")

	exePath, err := os.Executable()
	if err != nil {
		log.Fatal(err.Error())
	}
	projectPath := filepath.Dir(filepath.Dir(exePath))
	serverPath := fmt.Sprint(projectPath, "/daemon/server.py")
	log.Println(serverPath)

	cmd := exec.Command(config.PythonInterpreter, serverPath, config.TransformerName)
	cmd.Env = append(cmd.Env, fmt.Sprint("HOME=", os.Getenv("HOME")), fmt.Sprint("PYTHONPATH=", projectPath))
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
	var lim int
	if limit == "" {
		lim = 10
	} else {
		var err error
		lim, err = strconv.Atoi(limit)
		if err != nil || lim < 1 {
			return echo.NewHTTPError(http.StatusBadRequest, "limit must be a positive integer")
		}
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
	file := utils.OpenLogFile("daemon.log")
	logger := slog.New(slog.NewJSONHandler(file, nil))
	e.Use(middleware.RequestLoggerWithConfig(middleware.RequestLoggerConfig{
		LogStatus:   true,
		LogURI:      true,
		LogError:    true,
		HandleError: true, // forwards error to the global error handler, so it can decide appropriate status code
		LogValuesFunc: func(_ echo.Context, v middleware.RequestLoggerValues) error {
			if v.Error == nil {
				logger.LogAttrs(context.Background(), slog.LevelInfo, "REQUEST",
					slog.String("uri", v.URI),
					slog.Int("status", v.Status),
				)
			} else {
				logger.LogAttrs(context.Background(), slog.LevelError, "REQUEST_ERROR",
					slog.String("uri", v.URI),
					slog.Int("status", v.Status),
					slog.String("err", v.Error.Error()),
				)
			}
			return nil
		},
	}))

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
