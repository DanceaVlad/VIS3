import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { feature } from "https://cdn.jsdelivr.net/npm/topojson@3/+esm";

let bundeslanderNames;
let bunderslanderDeaths;

async function loadTotalDeaths() {
    try {
        const data = await d3.csv("../data/cleaned_csvs/choropleth_deaths_per_1000_people_sum_sep_22.csv", d3.autoType);
        bundeslanderNames = data.map(d => d.Bundesland);
        bunderslanderDeaths = data.reduce((acc, d) => {
            acc[d.Bundesland] = d['sum_deaths_per_1000_people'];
            return acc;
        }, {});
    } catch (error) {
        console.error('Error loading the CSV file:', error);
    }
}


async function loadAustriaMap() {
    try {
        const data = await d3.json("../data/Austria.topo.json");
        const objectName = Object.keys(data.objects)[0]; // Get the first object key
        const austria = feature(data, data.objects[objectName]);

        const svg = d3.select('#map')
        const projection = d3.geoMercator().fitSize([+svg.attr("width"), +svg.attr("height")], austria);
        const path = d3.geoPath().projection(projection);

        // Define a color scale
        const deathValues = Object.values(bunderslanderDeaths);
        const colorScale = d3.scaleLinear()
            .domain([d3.min(deathValues), d3.max(deathValues)])
            .range(["white", "red"]);

        svg.append("g")
            .selectAll("path")
            .data(austria.features)
            .join("path")
            .attr("d", path)
            .attr("fill", d => {
                const bundeslandName = d.properties.name;
                const deaths = bunderslanderDeaths[bundeslandName];
                return colorScale(deaths);
            })
            .attr("stroke", "#333");

        austria.features.forEach((feature) => {
            const [x, y] = projection(d3.geoCentroid(feature));
            const bundeslandName = feature.properties.name;
            const deaths = bunderslanderDeaths[bundeslandName];

            svg.append("text")
                .attr("x", x)
                .attr("y", y)
                .attr("dy", "0.35em")
                .text(`${deaths.toFixed(2)}`)
                .attr("font-size", 10)
                .attr("text-anchor", "middle");
        });
    } catch (error) {
        console.error("Error loading or processing data:", error);
    }
}

async function initialize() {
    await loadTotalDeaths();
    await loadAustriaMap();
}

initialize();
