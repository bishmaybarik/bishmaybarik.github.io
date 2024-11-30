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
        // Mapping repository names to custom titles
        const repositories = [
            {
                repo: "bishmaybarik/dist_concord_aidis_2003-13",
                title: "District Concordance Codes for AIDIS 2003 and AIDIS 2013",
                description: "There are many new districts states created between the year 2003 and 2013 in India. However, for equivalent comparison of economic parameters, I have concorded the districts of both AIDIS 2003 and AIDIS 2013. The STATA codes for district concordance can be found in this repository."
            },
            {
                repo: "bishmaybarik/ginicoeff_india",
                title: "Gini Coefficients for Monthly Per Capita Consumption Expenditure - Indian Districts",
                description: "This repository contains code for calculating the Monthly Per Capita Consumption Expenditure Gini Coefficients across various districts in India, with the aim of visualizing the results through a heatmap."
            },
            {
                repo: "bishmaybarik/income-pyramids-clean",
                title: "Cleaned Data - Income Pyramids_dx - CMIE",
                description: "Cleaning the CMIE Income Pyramids datasets by first converting the CSV files into .dta files, and then appending the datasets to create a panel dataset."
            },
            {
                repo: "bishmaybarik/ngram-code",
                title: "Code for District Matching - Using N-Gram and Jaccard Similarities",
                description: "This is a simple code for matching districts across two datasets (CSV), with associated probability of matching."
            }
        ];

        const container = document.getElementById("repositories");

        for (const { repo, title, description } of repositories) {
            const data = await fetchGitHubRepo(repo);
            if (data) {
                container.innerHTML += `
                    <div class="repository-card">
                        <a href="${data.html_url}" target="_blank">
                            <h3>${title}</h3>
                            <p>${description}</p>
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
