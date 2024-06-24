import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

let vorarlbergDeaths;
let kaerntenDeaths;

async function loadVorarlbergDeaths() {
    try {
        const data = await d3.csv("../data/cleaned_csvs/mortality_rate_per_1000_cases_Vorarlberg.csv", d => {
            return {
                Datum: d3.timeParse("%Y-%m-%d")(d.Datum),
                Vorarlberg: +d.Vorarlberg
            };
        });
        vorarlbergDeaths = data;
    } catch (error) {
        console.error('Error loading the CSV file:', error);
    }
}

async function loadKaerntenDeaths() {
    try {
        const data = await d3.csv("../data/cleaned_csvs/mortality_rate_per_1000_cases_Kaernten.csv", d => {
            return {
                Datum: d3.timeParse("%Y-%m-%d")(d.Datum),
                Kaernten: +d.Kärnten
            };
        });
        kaerntenDeaths = data;
    } catch (error) {
        console.error('Error loading the CSV file:', error);
    }
}

async function loadTimeline() {
    // Wait for the data to be loaded
    await Promise.all([loadVorarlbergDeaths(), loadKaerntenDeaths()]);

    // Merge the datasets based on the date
    const mergedData = vorarlbergDeaths.map(v => {
        const k = kaerntenDeaths.find(k => k.Datum.getTime() === v.Datum.getTime());
        return { Datum: v.Datum, Vorarlberg: v.Vorarlberg, Kaernten: k ? k.Kaernten : null };
    });

    // line chart with Vorarlberg and Kaernten
    const svg = d3.select("#timeline");
    const width = +svg.attr("width");
    const height = +svg.attr("height");
    const margin = { top: 40, right: 40, bottom: 60, left: 100 }; // Increased margins
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // death data structure: "Datum";"Vorarlberg"
    const xValue = d => d.Datum;
    const yValue = d => d.Vorarlberg;
    const yValue2 = d => d.Kaernten;

    const xScale = d3.scaleTime()
        .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
        .range([innerHeight, 0]);

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const xAxis = d3.axisBottom(xScale)
        .tickSize(6) // Short ticks
        .tickPadding(15)
        .tickFormat(d3.timeFormat("%b %Y")); // Custom tick format

    const yAxis = d3.axisLeft(yScale)
        .tickSize(6) // Short ticks
        .tickPadding(10);

    const lineGenerator = d3.line()
        .x(d => xScale(xValue(d)))
        .y(d => yScale(yValue(d)))
        .curve(d3.curveBasis);

    const lineGenerator2 = d3.line()
        .x(d => xScale(xValue(d)))
        .y(d => yScale(yValue2(d)))
        .curve(d3.curveBasis);

    xScale.domain(d3.extent(mergedData, xValue));
    yScale.domain([0, d3.max(mergedData, d => Math.max(yValue(d), yValue2(d)))]);

    g.append("g")
        .call(yAxis)
        .selectAll(".domain")
        .style("stroke", "#333");

    g.append("g")
        .call(xAxis)
        .attr("transform", `translate(0,${innerHeight})`)
        .selectAll(".domain")
        .style("stroke", "#333");

    g.append("path")
        .attr("class", "line-path")
        .attr("d", lineGenerator(mergedData))
        .style("stroke", "blue");

    g.append("path")
        .attr("class", "line-path")
        .attr("d", lineGenerator2(mergedData))
        .style("stroke", "red");

    // Add vertical line for vaccination start
    const vaccinationDate = new Date(2020, 11, 27); // December 27, 2020
    g.append("line")
        .attr("x1", xScale(vaccinationDate))
        .attr("y1", 0)
        .attr("x2", xScale(vaccinationDate))
        .attr("y2", innerHeight)
        .attr("stroke", "green")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", "4 4");

    g.append("text")
        .attr("x", xScale(vaccinationDate) + 5)
        .attr("y", 15)
        .attr("fill", "green")
        .attr("font-size", "12px")
        .text("Vaccination start");

    g.append("text")    
        .attr("class", "title")
        .attr("x", innerWidth / 2)
        .attr("y", -20) // Adjusted position
        .attr("text-anchor", "middle") // Centered text
        .text("Deaths per 1000 cases in Vorarlberg and Kaernten");

    g.append("text")
        .attr("class", "x-axis-label")
        .attr("x", innerWidth / 2)
        .attr("y", innerHeight + 50) // Adjusted position
        .attr("text-anchor", "middle") // Centered text
        .text("Date");

    g.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("x", -innerHeight / 2)
        .attr("y", -50) // Adjusted position
        .attr("text-anchor", "middle") // Centered text
        .text("Deaths per 1000 cases");

    g.append("text")
        .attr("class", "legend")
        .attr("x", innerWidth - 200)
        .attr("y", 20)
        .text("Vorarlberg")
        .style("fill", "blue");

    g.append("text")
        .attr("class", "legend")
        .attr("x", innerWidth - 200)
        .attr("y", 40)
        .text("Kaernten")
        .style("fill", "red");

    g.selectAll(".tick line")
        .style("stroke", "#333");

    g.selectAll(".line-path")
        .style("fill", "none")
        .style("stroke-width", 2)
        .style("stroke-linejoin", "round")
        .style("stroke-linecap", "round");

    g.selectAll(".title")
        .style("font-size", "1.5em");

    g.selectAll(".x-axis-label, .y-axis-label")
        .style("font-size", "1.2em");

    g.selectAll(".legend")
        .style("font-size", "1.2em");
}

async function initialize() {
    await loadTimeline();
}

initialize();
