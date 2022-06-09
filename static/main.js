function main() {

    d3.json("../static/graph.json").then(data => {
        const links = data.links.map(d => Object.create(d));
        const nodes = data.nodes.map(d => Object.create(d));

        console.log(nodes)
        console.log(links)

        width = 3000
        height = 1000
        //color = "#aaaaaa"
        
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(function(d){
                console.log(d)
                return d.id

            }))
            .force("charge", d3.forceManyBody())
            .force("x", d3.forceX())
            .force("y", d3.forceY());

        const svg = d3.select("body").append("svg")
            .attr("viewBox", [-width / 2, -height / 2, width, height]);
      
        const link = svg.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke-width", d => Math.sqrt(d.value));


        const node = svg.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", 5)
            .attr("fill", function(d){
                const scale = d3.scaleOrdinal(d3.schemeCategory10);
                return scale(d.group);
            })
            .call(drag(simulation));
      
        node.append("title")
            .text(d => d.id);
      
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
        
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });
      
        //invalidation.then(() => simulation.stop());


        svg.node();

    });
}

color = {
    
}

drag = simulation => {
  
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event,d) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event,d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    
    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
  }