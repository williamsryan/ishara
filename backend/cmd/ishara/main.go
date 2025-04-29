package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/williamsryan/ishara/internal/handlers"
)

func main() {
	// Load environment variables from .env
	if err := godotenv.Load(); err != nil {
		log.Fatal("Error loading .env file")
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	r := gin.Default()

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// OAuth and Sheets API routes
	r.GET("/api/auth/google/login", handlers.GoogleLogin)
	r.GET("/api/auth/google/callback", handlers.GoogleCallback)
	r.GET("/api/sheets/list", handlers.ListSheets)

	r.Run(":" + port)
}
