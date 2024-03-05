package cartographer

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"log/slog"
	"net/http"
	"os"
	"strconv"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"github.com/chaitanyabsprip/cartographer/utils"
)

func index(c echo.Context) error {
	filepath := c.QueryParam("filepath")
	Index(filepath)
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
	out, err := Search(query, lim)
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

func Serve() {
	e := echo.New()
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Pre(middleware.RemoveTrailingSlash())

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

	e.GET("/index", index)
	e.GET("/search", search)
	e.GET("/health", health)
	e.GET("/info", info)
	data, err := json.MarshalIndent(e.Routes(), "", "  ")
	if err != nil {
		log.Fatal(err.Error())
	}
	fmt.Print(string(data))
	log.Println("Server started")
	e.Logger.Fatal(e.Start("0.0.0.0:30001"))
}
