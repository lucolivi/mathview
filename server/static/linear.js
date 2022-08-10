function main(theorem) {

    d3.json("../theorem/" + theorem).then(data => {
        
        const links = data.hyps.map(function(d) {
            //console.log(d)
            var linkObj = {
                "source":d[0],
                "target":d[1]
            }

            return Object.create(linkObj)
        });
        
        const nodes = data.steps.map(function(d) {
            //console.log(d)
            d.id = d.step
            //console.log(d)
            return Object.create(d)
        });

        hyps_dict = []
        for(i = 0; i < data.hyps.length; i++) {
            source = data.hyps[i][0]
            target = data.hyps[i][1]

            if(!(source in hyps_dict))
                hyps_dict[source] = []
            
            hyps_dict[source].push(target)
        }

        console.log(hyps_dict)



        //console.log(nodes)
        //console.log(links)

        // width = 1500
        // height = 800
        // //color = "#aaaaaa"
        
        // const simulation = d3.forceSimulation(nodes)
        //     .force("link", d3.forceLink(links).id(function(d){
        //         //console.log(d)
        //         return d.id
        //     }))
        //     .force("charge", d3.forceManyBody().strength(-1000))
        //     .force("x", d3.forceX())
        //     .force("y", d3.forceY());

        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const thres = parseInt(urlParams.get('t'))


        d3.select("body").append("div")
            .selectAll("p")
                .data(nodes)
                .join("p")
                .style("text-decoration", function(d){
                    if(d.lemma_log_complexity < thres)
                        return "line-through"
                })
                // .style("font-weight", function(d){
                //     if(d.lemma_log_complexity >= thres)
                //         return "bold"
                // })
                .text(d => "[" + (hyps_dict[d.step] || "") + "] " + d.step + " - " + d.theorem + " " + d.expression + " - " + d.lemma_log_complexity)

        // const svg = d3.select("body").append("svg")
        //     .style("font", "12px sans-serif");

        // const g = svg.append("g");

        // svg.attr("viewBox", [-width / 2, -height / 2, width, height]);

        // const zoom = d3.zoom()
        //     .scaleExtent([0.5, 8])
        //     .on("zoom", zoomed);

        // function zoomed(event) {
        //     const {transform} = event;
        //     g.attr("transform", transform);
        //     g.attr("stroke-width", 1 / transform.k);
        // }

        // const types = ["licensing","suit","resolved"];
        // const color = d3.scaleOrdinal(types, d3.schemeCategory10)

//           // Per-type markers, as they don't inherit styles.
//   svg.append("defs").append("marker")
//     .attr("id", "arrows")
//     .attr("viewBox", "0 -5 10 10")
//     .attr("refX", 15)
//     .attr("refY", -0.5)
//     .attr("markerWidth", 6)
//     .attr("markerHeight", 6)
//     .attr("orient", "auto")
//   .append("path")
//     .attr("fill", "#aaaaaa")
//     .attr("d", "M0,-5L10,0L0,5");

            
        // svg.call(zoom);

        // const link = g.append("g")
        //     .attr("stroke", "#999")
        //     .attr("stroke-opacity", 0.6)
        //     .selectAll("line")
        //     .data(links)
        //     .join("line")
        //     .attr("stroke-width", 2)
        // .attr("marker-end", "url(#arrows)");
            

        //     const link = svg.append("g")
        //     .attr("fill", "#999")
        //     .attr("stroke-width", 1.5)
        //   .selectAll("path")
        //   .data(links)
        //   .join("path")
        //     .attr("stroke", "#999")
        //     .attr("marker-end", "url(#arrows)");

        // const node = g.append("g")
        //     .attr("stroke", "#fff")
        //     .attr("stroke-width", 1.5)


        // var node = g.append("g")
        //     //.attr("fill", "#aaaaaa")
        //     //.attr("stroke-linecap", "round")
        //     //.attr("stroke-linejoin", "round")
        //     .selectAll("g")
        //     .data(nodes)
        //     .join("g")

            
        // node.call(drag(simulation))
            
        // node.append("circle")
        //     .attr("stroke", "white")
        //     .attr("stroke-width", 1.5)
        //     .attr("r", 10)
        //     .attr("fill", function(d){
        //         const scale = d3.scaleOrdinal(d3.schemeCategory10);
        //         return scale(d.group);
        //     })
            

        // node.append("text")
        //     .attr("x", 8)
        //     .attr("y", "0.31em")
        //     .text(d => d.step + " - " + d.theorem + " " + d.expression)
        //   .clone(true).lower()
        //     .attr("fill", "none")
        //     .attr("stroke", "white")
        //     .attr("stroke-width", 3);

        // node.append("text")
        //     .attr("x", 8)
        //     .attr("y", "1.51em")
        //     .text(d => d.norm_complexity + " - " + d.log_complexity)
        //   .clone(true).lower()
        //     .attr("fill", "none")
        //     .attr("stroke", "white")
        //     .attr("stroke-width", 3);

      
        // simulation.on("tick", () => {
        //     link
        //         .attr("x1", d => d.source.x)
        //         .attr("y1", d => d.source.y)
        //         .attr("x2", d => d.target.x)
        //         .attr("y2", d => d.target.y);
        //     node.attr("transform", d => `translate(${d.x},${d.y})`);
        //     // node
        //     //     .attr("cx", d => d.x)
        //     //     .attr("cy", d => d.y);
        // });
      
        //invalidation.then(() => simulation.stop());


        // g.node();

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
        //.on("end", dragended);
  }