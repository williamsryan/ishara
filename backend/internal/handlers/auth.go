package handlers

import (
	"context"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"

	"google.golang.org/api/drive/v3"
	"google.golang.org/api/option"
)

func getGoogleOauthConfig() *oauth2.Config {
	return &oauth2.Config{
		RedirectURL:  "http://localhost:8080/api/auth/google/callback",
		ClientID:     os.Getenv("GOOGLE_CLIENT_ID"),
		ClientSecret: os.Getenv("GOOGLE_CLIENT_SECRET"),
		Scopes: []string{
			"https://www.googleapis.com/auth/drive.readonly",
		},
		Endpoint: google.Endpoint,
	}
}

// TEMPORARY in-memory token store
var userToken *oauth2.Token

func GoogleLogin(c *gin.Context) {
	config := getGoogleOauthConfig()
	url := config.AuthCodeURL("state-token", oauth2.AccessTypeOffline)
	c.Redirect(http.StatusTemporaryRedirect, url)
}

func GoogleCallback(c *gin.Context) {
	ctx := context.Background()
	code := c.Query("code")
	config := getGoogleOauthConfig()

	token, err := config.Exchange(ctx, code)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to exchange token"})
		return
	}

	userToken = token
	c.Redirect(http.StatusTemporaryRedirect, "http://localhost:3000")
}

func ListSheets(c *gin.Context) {
	if userToken == nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Not authenticated"})
		return
	}

	ctx := context.Background()
	config := getGoogleOauthConfig()
	client := config.Client(ctx, userToken)

	srv, err := drive.NewService(ctx, option.WithHTTPClient(client))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create Drive service"})
		return
	}

	files, err := srv.Files.List().
		Q("mimeType='application/vnd.google-apps.spreadsheet'").
		Fields("files(id, name)").
		Do()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list spreadsheets"})
		return
	}

	c.JSON(http.StatusOK, files.Files)
}
