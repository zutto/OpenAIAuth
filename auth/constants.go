package auth

import (
	"os"
	"strings"

	"github.com/google/uuid"
)

const ios_app_version = "1744"
const device_token = "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"

var ios_device_id string

func init() {
	// Capitalize all letters
	ios_device_id = strings.ToUpper(uuid.New().String())

	if os.Getenv("IOS_DEVICE_ID") != "" {
		ios_device_id = os.Getenv("IOS_DEVICE_ID")
	}
}
