async function loadDashboard() {
    const connectionStatus =
        document.getElementById("connection-status");

    try {
        const health = await checkDatabaseHealth();

        connectionStatus.textContent =
            health.database === "connected"
                ? "Database Connected"
                : "Database Disconnected";

        const stats = await getDatabaseStats();

        document.getElementById("total-employees")
            .textContent =
            Number(stats.total_employees).toLocaleString();

        document.getElementById("total-departments")
            .textContent = stats.total_departments;

        document.getElementById("average-salary")
            .textContent =
            "₹" + Number(
                stats.salary_statistics.average_salary
            ).toLocaleString("en-IN", {
                maximumFractionDigits: 2
            });

        document.getElementById("database-status")
            .textContent = health.status;

    } catch (error) {
        connectionStatus.textContent = "Connection Failed";
        console.error("Dashboard error:", error);
    }
}
