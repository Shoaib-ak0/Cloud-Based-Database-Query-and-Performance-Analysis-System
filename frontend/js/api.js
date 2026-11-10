const API_BASE_URL = "/api";

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        },
        ...options
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Something went wrong"
        );
    }

    return data;
}

async function checkDatabaseHealth() {
    return apiRequest("/health");
}

async function getDatabaseStats() {
    return apiRequest("/database/stats");
}

async function executeQuery(query) {
    return apiRequest("/query/execute", {
        method: "POST",
        body: JSON.stringify({ query })
    });
}

async function runBenchmark(department, iterations) {
    return apiRequest("/benchmark/compare", {
        method: "POST",
        body: JSON.stringify({
            department,
            iterations: Number(iterations)
        })
    });
}

async function createIndex(){
	return apiRequest("/index/create",{
		method: "POST"
});
}

async function deleteIndex(){
	return apiRequest("/index/delete",{
	method: "DELETE"
});
}
