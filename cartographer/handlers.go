package cartographer

import (
	"fmt"
	"net/http"
	"os"
	"strconv"

	"github.com/labstack/echo/v4"
)

func index(c echo.Context) error {
	filepath := c.QueryParam("filepath")
	err := Index(filepath)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, err.Error())
	}
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
