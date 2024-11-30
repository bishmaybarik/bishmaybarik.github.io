---
layout: default
title: Public Goods
---

# Public Goods: Selected GitHub Repositories

Here are some of the projects I’ve worked on that I’d like to showcase. The repository data below is fetched live from GitHub!

<div id="repositories"></div>

<script>
    async function fetchGitHubRepo(repo) {
        const response = await fetch(`https://api.github.com/repos/${repo}`);
        if (!response.ok) {
            console.error(`Failed to fetch repo ${repo}`);
            return null;
        }
        return response.json();
    }

    async function displayRepositories() {
        const repositories = [
            "bishmaybarik/dist_concord_aidis_2003-13",
            "bishmaybarik/ginicoeff_india",
            "bishmaybarik/income-pyramids-clean",
            "bishmaybarik/ngram-code"
        ];

        const container = document.getElementById("repositories");

        for (const repo of repositories) {
            const data = await fetchGitHubRepo(repo);
            if (data) {
                container.innerHTML += `
                    <div class="repository-card">
                        <a href="${data.html_url}" target="_blank">
                            <h3>${data.name}</h3>
                            <p>${data.description || "No description provided."}</p>
                            <div class="repo-stats">
                                <span>⭐ ${data.stargazers_count} Stars</span>
                                <span>🍴 ${data.forks_count} Forks</span>
                                <span>👀 ${data.watchers_count} Watchers</span>
                            </div>
                        </a>
                    </div>
                `;
            }
        }
    }

    displayRepositories();
</script>

<style>
    #repositories {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 20px;
    }
    .repository-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        background-color: #ffffff;
        width: 45%;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out;
        position: relative;
    }
    .repository-card:hover {
        transform: translateY(-10px);
    }
    .repository-card h3 {
        margin: 0 0 10px;
        color: #0366d6;
    }
    .repository-card p {
        margin: 0 0 10px;
        color: #586069;
    }
    .repo-stats {
        display: flex;
        gap: 15px;
        font-size: 0.9em;
        color: #586069;
    }
</style>
