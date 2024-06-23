import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { feature } from "https://cdn.jsdelivr.net/npm/topojson@3/+esm";

let bundeslanderNames;
let bundeslanderPopulations;

async function loadPopulation() {
    try {
        const data = await d3.csv("../data/datasets/optional_original_sources/population_by_bundesland.csv", d3.autoType);
        console.log(data);
        bundeslanderNames = data.map(d => d.Bundesland);
        bundeslanderPopulations = data.reduce((acc, d) => {
            acc[d.Bundesland] = d['01.01.2020'];
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
        const populationValues = Object.values(bundeslanderPopulations);
        const colorScale = d3.scaleLinear()
            .domain([d3.min(populationValues), d3.max(populationValues)])
            .range(["white", "red"]);

        svg.append("g")
            .selectAll("path")
            .data(austria.features)
            .join("path")
            .attr("d", path)
            .attr("fill", d => {
                const bundeslandName = d.properties.name;
                const population = bundeslanderPopulations[bundeslandName];
                return colorScale(population);
            })
            .attr("stroke", "#333");

        austria.features.forEach((feature) => {
            const [x, y] = projection(d3.geoCentroid(feature));
            const bundeslandName = feature.properties.name;
            const population = bundeslanderPopulations[bundeslandName];

            svg.append("text")
                .attr("x", x)
                .attr("y", y)
                .attr("dy", "0.35em")
                .text(`${population}`)
                .attr("font-size", 10)
                .attr("text-anchor", "middle");
        });
    } catch (error) {
        console.error("Error loading or processing data:", error);
    }
}

async function initialize() {
    await loadPopulation();
    await loadAustriaMap();
}

initialize();
