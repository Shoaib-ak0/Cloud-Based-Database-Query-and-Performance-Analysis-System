function renderPerformanceChart(withoutIndex, withIndex) {
    const canvas = document.getElementById("performance-chart");

    if (!canvas) {
        console.error("Performance chart canvas not found.");
        return;
    }

    const ctx = canvas.getContext("2d");

    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    const values = [
        withoutIndex,
        withIndex
    ];

    const labels = [
        "Without Index",
        "With Index"
    ];

    const maxValue = Math.max(...values) * 1.2;
    const barWidth = 100;
    const gap = 100;

    const startX = (width - (2 * barWidth + gap)) / 2;
    const baseY = height - 50;
    const chartHeight = height - 100;

    ctx.font = "14px Arial";
    ctx.fillStyle = "#94a3b8";
    ctx.textAlign = "center";

    values.forEach((value, i) => {
        const barHeight = (value / maxValue) * chartHeight;
        const x = startX + i * (barWidth + gap);
        const y = baseY - barHeight;

        ctx.fillStyle = i === 0 ? "#f59e0b" : "#3b82f6";
        ctx.fillRect(x, y, barWidth, barHeight);

        ctx.fillStyle = "#ffffff";
        ctx.fillText(value.toFixed(2) + " ms", x + barWidth / 2, y - 10);

        ctx.fillStyle = "#94a3b8";
        ctx.fillText(labels[i], x + barWidth / 2, baseY + 25);
    });
}
