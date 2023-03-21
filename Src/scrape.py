import os
import base64
import re
from github import Github
from dotenv import load_dotenv

load_dotenv()

# Replace with your GitHub username and access token
username = 'otdavies'
access_token = os.getenv('GH_TOKEN')

# Set the name of the optional blog file in your repositories
blog_filename = 'README.md'

# Set the path to the content folder in your blog project
content_path = 'content'

# Create a GitHub API connection
gh = Github(access_token)
user = gh.get_user(username)

# Fetch all public repositories
repos = user.get_repos()

# Regular expression to find image URLs
image_pattern = re.compile(r'\!\[.*\]\((.+)\)')


def split_variable_name(variable_name):
    # Replace dashes and underscores with spaces
    readable_name = re.sub(r"[-_]", " ", variable_name)

    # Put a space infront of each capital letter that isn't followed by other capital letters
    readable_name = re.sub(r"([A-Z])(?=[a-z])", r" \1", readable_name)

    # Put a space infront of a group of numbers
    readable_name = re.sub(r"(\d+)", r" \1", readable_name)

    # Split the string by spaces
    words = readable_name.split()

    # Capitalize the first letter of each word, but keep acronyms intact
    capitalized_words = []
    for word in words:
        if word.isupper():
            capitalized_words.append(word)
        else:
            capitalized_words.append(word.capitalize())

    # Join the words to form the final human-readable name
    human_readable_name = " ".join(capitalized_words)

    return human_readable_name


def scrape():
    for repo in repos:
        if not repo.private:
            # Check if the "blog" file exists in the repo
            try:
                blog_file = repo.get_contents(blog_filename)
                content = base64.b64decode(blog_file.content).decode('utf-8')
            except:
                # Skip if the repo doesn't have the "blog" file
                continue

            # Extract the first image URL
            image_url = None
            match = image_pattern.search(content)
            if match:
                image_url = match.group(1)

            # Create a blog post file from the "blog" file content
            file_name = f"{repo.name}.md"
            file_path = os.path.join(content_path, file_name)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Title: {split_variable_name(repo.name)}\n")
                f.write(f"Date: {repo.created_at}\n")
                f.write(f"Modified: {repo.updated_at}\n")
                # If the repo language is None, use "Other"
                f.write(
                    f"Category: {repo.language if repo.language else 'Other'}\n")
                f.write(f"Thumbnail: {image_url}\n")
                # Get languages as tags
                f.write(f"Tags: {', '.join(repo.get_languages().keys())}\n")
                f.write(content)
    print("Fetched blog files successfully.")


if __name__ == "__main__":
    scrape()
