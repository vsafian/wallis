document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("weekOrdersChart")) {

        let weekOrdersChart = new Chartist.Line('#weekOrdersChart', {
            labels: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            series: orderStats.series
        }, {
            lineSmooth: Chartist.Interpolation.cardinal({
                tension: 0
            }),
            low: 0,
            high: 100,
            chartPadding: {
                top: 0,
                right: 0,
                bottom: 0,
                left: 0
            },
        });

        md.startAnimationForLineChart(weekOrdersChart);
    }
});