package cartographer

import (
	"context"
	"errors"
	"fmt"
	"log"
	"log/slog"
	"net"
	"net/http"
	"os"
	"path"
	"strconv"

	"github.com/kirsle/configdir"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"github.com/chaitanyabsprip/cartographer/utils"
)

func Serve() {
	e := echo.New()
	setupLoggingMiddleware(e)
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Pre(middleware.RemoveTrailingSlash())

	e.GET("/index", index)
	e.GET("/search", search)
	e.GET("/health", health)
	e.GET("/info", info)

	listener, err := net.Listen("tcp", "127.0.0.1:0") // 0 tells the system to select an available port
	if err != nil {
		log.Fatal("Error starting server: ", err.Error())
	}
	defer listener.Close()
	port := listener.Addr().(*net.TCPAddr).Port
	fmt.Println("Server is running on port:", port)
	savePort(port)
	go serve(e, listener)
	printRoutes(e.Routes())
	log.Println("Server started")
	select {}
}

func setupLoggingMiddleware(e *echo.Echo) {
	file := utils.OpenLogFile("daemon.log")
	logger := slog.New(slog.NewJSONHandler(file, nil))
	e.Use(middleware.RequestLoggerWithConfig(middleware.RequestLoggerConfig{
		LogStatus:   true,
		LogURI:      true,
		LogError:    true,
		HandleError: true,
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
}

func savePort(port int) {
	cacheDir := configdir.LocalCache("cartographer")
	cacheFilepath := path.Join(cacheDir, ".port")
	err := os.WriteFile(cacheFilepath, []byte(strconv.Itoa(port)), 0o644)
	if err != nil {
		log.Fatal("Error writing port to file:", err)
	}
}

func serve(e *echo.Echo, listener net.Listener) {
	s := http.Server{Handler: e}
	if err := s.Serve(listener); err != nil && !errors.Is(err, http.ErrServerClosed) {
		e.Logger.Fatal(err)
	}
}

func printRoutes(routes []*echo.Route) {
	for _, route := range routes {
		fmt.Printf("%s %s\n", route.Method, route.Path)
	}
}
