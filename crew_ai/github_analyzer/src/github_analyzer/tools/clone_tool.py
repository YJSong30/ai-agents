from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os

class GitCloneInput(BaseModel):
    """Input schema for GitCloneTool."""
    repo_url: str = Field(..., description="GitHub repository URL")
    target_dir: str = Field(..., description="Local directory path to clone into")
    branch: str = Field(default="main", description="Branch to clone (default: main)")

class GitCloneTool(BaseTool):
    name: str = "git_clone_tool"
    description: str = "Clone a Git repository to a local directory with branch selection"
    args_schema: Type[BaseModel] = GitCloneInput

    def _run(self, repo_url: str, target_dir: str, branch: str = "main") -> str:
        """
        Clone a git repository to a local directory.

        Args:
            repo_url: GitHub repository URL
            target_dir: Local directory path to clone into
            branch: Branch to clone (default: main)

        Returns:
            Success/error message
        """
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_dir, exist_ok=True)

            # Prepare git clone command
            cmd = ["git", "clone", "-b", branch, repo_url, target_dir]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=500)

            if result.returncode == 0:
                return f"Successfully cloned {repo_url} to {target_dir} on branch {branch}"
            else:
                return f"Failed to clone {repo_url} to {target_dir} on branch {branch}. Error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return f"Clone operation timed out for {repo_url} to {target_dir} on branch {branch}"
        except Exception as e:
            return f"An error occurred while cloning {repo_url} to {target_dir} on branch {branch}. Error: {str(e)}"

# Create instance of tool to use in Agent
git_clone_tool = GitCloneTool()