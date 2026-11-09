document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();

    const executeButton = document.getElementById(
        "execute-query-btn");

    executeButton.addEventListener("click", handleQueryExecution);
	const benchmarkButton = document.getElementById(
	"run-benchmark-btn");

	benchmarkButton.addEventListener("click",handleBenchmark);
	
	const createIndexButton = document.getElementById("create-index-btn");
	const deleteIndexButton = document.getElementById("delete-index-btn");

	createIndexButton.addEventListener("click", handleCreateIndex);
	deleteIndexButton.addEventListener("click", handleDeleteIndex);
});

async function handleQueryExecution() {
    const query = document.getElementById("sql-query").value.trim();
    const button = document.getElementById("execute-query-btn");
    const message = document.getElementById("query-message");
    const resultsContainer = document.getElementById("query-results");

    if (!query) {
        message.textContent = "Please enter a SQL query.";
        return;
    }

    button.disabled = true;
    button.textContent = "Executing...";
    message.textContent = "";

    try {
        const data = await executeQuery(query);

        if (data.status !== "success") {
            throw new Error("Query execution failed.");
        }

        displayQueryResults(data);

        message.textContent =
            `Success: ${data.rows_returned} rows returned in ${data.execution_time_ms} ms.`;

    } catch (error) {
        resultsContainer.textContent = "";
        message.textContent = `Error: ${error.message}`;

    } finally {
        button.disabled = false;
        button.textContent = "Execute Query";
    }
}

function displayQueryResults(data) {
    const container = document.getElementById("query-results");

    if (!data.results || data.results.length === 0) {
        container.textContent = "No records found.";
        return;
    }

    const columns = Object.keys(data.results[0]);

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    columns.forEach(column => {
        const th = document.createElement("th");
        th.textContent = column;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    data.results.forEach(record => {
        const row = document.createElement("tr");

        columns.forEach(column => {
            const td = document.createElement("td");
            td.textContent = record[column] ?? "NULL";
            row.appendChild(td);
        });

        tbody.appendChild(row);
    });

    table.appendChild(tbody);

    container.replaceChildren(table);
}
 async function handleBenchmark() {
    const department = document.getElementById("department").value;
    const iterations = Number(
	document.getElementById("iterations").value
);

    const button = document.getElementById("run-benchmark-btn");
    const results = document.getElementById("benchmark-results");

    if (iterations < 5 || iterations > 30) {
        results.textContent = "Iterations must be between 5 and 30.";
        return;
    }

    button.disabled = true;
    button.textContent = "Running Benchmark...";

    results.textContent = "Running performance tests...";

    try {
        const data = await runBenchmark(department, iterations);

        const withoutIndex = data.without_index;
        const withIndex = data.with_index;
	renderPerformanceChart(
		withoutIndex.median_execution_time_ms,
		withIndex.median_execution_time_ms
);

        results.innerHTML = `
            <h3>Benchmark Results</h3>

            <div class="benchmark-cards">

                <div class="benchmark-card">
                    <h4>Without Index</h4>
                    <p>${withoutIndex.median_execution_time_ms.toFixed(3)} ms</p>
                    <span>Full table scan</span>
                </div>

                <div class="benchmark-card">
                    <h4>With Index</h4>
                    <p>${withIndex.median_execution_time_ms.toFixed(3)} ms</p>
                    <span>Index lookup</span>
                </div>

                <div class="benchmark-card">
                    <h4>Improvement</h4>
                    <p>${data.improvement_percent.toFixed(2)}%</p>
                    <span>Performance improvement</span>
                </div>

            </div>

            <p>
                Department: ${department}
                | Iterations: ${data.iterations_per_condition}
            </p>
        `;

    } catch (error) {
        results.textContent = "Benchmark failed: " + error.message;
        console.error(error);

    } finally {
        button.disabled = false;
        button.textContent = "Run Comparison";
    }
}
async function handleCreateIndex() {
    const message = document.getElementById("index-message");

    try {
        message.textContent = "Creating index...";

        const data = await createIndex();

        message.textContent = data.message;
    } catch (error) {
        message.textContent = "Error: " + error.message;
    }
}

async function handleDeleteIndex() {
    const message = document.getElementById("index-message");

    try {
        message.textContent = "Deleting index...";

        const data = await deleteIndex();

        message.textContent = data.message;
    } catch (error) {
        message.textContent = "Error: " + error.message;
    }
}
