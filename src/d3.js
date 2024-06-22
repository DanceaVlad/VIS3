import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { feature } from "https://cdn.jsdelivr.net/npm/topojson@3/+esm";

// Load the TopoJSON file
d3.json("Austria.topo.json").then(data => {
    // Log the data to inspect its structure
    console.log("TopoJSON data:", data);

    // Adjust this part based on the actual structure of your TopoJSON file
    const objectName = Object.keys(data.objects)[0]; // Get the first object key
    console.log("Using object name:", objectName);

    // Convert TopoJSON to GeoJSON
    const austria = feature(data, data.objects[objectName]);

    // Log the GeoJSON data
    console.log("GeoJSON data:", austria);

    // Select the SVG element
    const svg = d3.select("svg");

    // Define a projection
    const projection = d3.geoMercator()
        .fitSize([+svg.attr("width"), +svg.attr("height")], austria);

    // Define a path generator
    const path = d3.geoPath().projection(projection);

    // Draw the map
    svg.append("g")
        .selectAll("path")
        .data(austria.features)
        .join("path")
        .attr("d", path)
        .attr("fill", "#ccc")
        .attr("stroke", "#333");

    // Add circles for testing
    austria.features.forEach(feature => {
        const [x, y] = projection(d3.geoCentroid(feature));
        svg.append("circle")
            .attr("cx", x)
            .attr("cy", y)
            .attr("r", 5)
            .attr("fill", "steelblue")
            .attr("stroke", "#333");
    });
}).catch(error => {
    console.error("Error loading or processing data:", error);
});
