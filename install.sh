#!/bin/bash

# Google Policy Reviewer Skill Installer
# Usage: ./install.sh [agent-name]

set -e

SKILL_NAME="google-policy-reviewer"
GITHUB_REPO="yourusername/google-policy-reviewer"  # 替换为你的GitHub用户名
AGENT=${1:-"openclaw"}

echo "🚀 Installing Google Policy Reviewer Skill for $AGENT..."

# Detect installation method
if command -v npx >/dev/null 2>&1; then
    echo "📦 Using npx skills CLI..."
    npx skills add "$GITHUB_REPO" -a "$AGENT"
    echo "✅ Installation complete!"
else
    echo "📦 Using manual installation..."
    
    # Determine skill directory based on agent
    case $AGENT in
        "openclaw")
            SKILL_DIR="$HOME/.openclaw/skills"
            ;;
        "claude-code")
            SKILL_DIR="$HOME/.claude/skills"
            ;;
        "cursor")
            SKILL_DIR="$HOME/.cursor/skills"
            ;;
        "cline")
            SKILL_DIR="$HOME/.cline/skills"
            ;;
        *)
            SKILL_DIR="./skills"
            echo "⚠️  Unknown agent '$AGENT', installing to ./skills/"
            ;;
    esac
    
    # Create directory if it doesn't exist
    mkdir -p "$SKILL_DIR"
    
    # Clone or download
    if [ -d "$SKILL_DIR/$SKILL_NAME" ]; then
        echo "🔄 Updating existing installation..."
        cd "$SKILL_DIR/$SKILL_NAME"
        git pull origin main
    else
        echo "📥 Downloading skill..."
        git clone "https://github.com/$GITHUB_REPO.git" "$SKILL_DIR/$SKILL_NAME"
    fi
    
    echo "✅ Installation complete!"
    echo "📍 Installed to: $SKILL_DIR/$SKILL_NAME"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Ask your AI assistant: 'Please help me review my app for Google policy compliance'"
echo "2. Or run the standalone script: python3 $SKILL_DIR/$SKILL_NAME/scripts/pre_submission_check.py"
echo ""
echo "📚 Documentation: https://github.com/$GITHUB_REPO"