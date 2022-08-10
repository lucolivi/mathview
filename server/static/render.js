//https://bl.ocks.org/d3noob/8375092


function main(theorem, threshold) {
    //console.log(threshold)

    d3.json("../theorem/" + theorem).then(data => {

        //console.log(data)

        //Filter nodes
        filtered_steps = []
        used_ids = []
        //console.log(data.steps)
        for(var i in data.steps) {

            //Ensure the last node always appear
            if(i == (data.steps.length - 1) || data.steps[i].edge_count_norm < threshold) {
            //if(['5', '7', '12', '14', '15'].includes(data.steps[i].step)) {
                filtered_steps.push(data.steps[i])
                used_ids.push(data.steps[i].step)
            }
        }

        //used_ids = ['2', '3', '5', '6', '7', '8', '9', '10', '12', '15']
        //console.log(used_ids)

        //Regenerate links according to the used ids

        hyps_dict = {}
        for(var i in data.hyps) {
            hyp = data.hyps[i]
            hyps_dict[hyp[1]] = hyp[0]
        }

        filtered_hyps = []
        for(var i in data.hyps) {
            source = data.hyps[i][0]
            target = data.hyps[i][1]
            
            if(used_ids.includes(target)) {
                while(!(used_ids.includes(source))) {
                    source = hyps_dict[source]
                    if(source == undefined)
                        break
                }

                filtered_hyps.push([i, source, target])
            }

        }

        //console.log(filtered_hyps)

        const nodes =  filtered_steps.map(function(d) {
            d.id = d.step

            // d.get_id = function() {
            //     return this.id
            // }

            //console.log(d)
            return Object.create(d)
        });


        const links = filtered_hyps.map(function(d) {
            var linkObj = {
                "id":d[0],
                "source":d[2],
                "target":d[1]
            }

            return Object.create(linkObj)
        });
        

        //console.log(nodes)
        //console.log(links)

        //color = "#aaaaaa"
        
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(function(d){
                //console.log(d)
                return d.id

                //return d.get_id()
            }))
            .force("charge", d3.forceManyBody().strength(-1000))
            .force("x", d3.forceX())
            .force("y", d3.forceY());

 
        // const node = g.append("g")
        //     .attr("stroke", "#fff")
        //     .attr("stroke-width", 1.5)


        var node = node_group
            //.attr("fill", "#aaaaaa")
            //.attr("stroke-linecap", "round")
            //.attr("stroke-linejoin", "round")
            .selectAll("g")
            .data(nodes, function(d) {
                //console.log(d)
                //return d.step
                //Use random ID so elements are recreated everytime
                return Math.round(Math.random() * 10000000)
            })
            .join("g")
            // .join(
            //     enter => enter.append("g")
            //         .append("text")
            //         .attr("x", 14)
            //         .attr("y", "0.31em")
            //         // .text(d => d.step + " - " + d.theorem + " " + d.expression)
            //         .text(d => d.theorem + " " + d.expression)
            //         //.clone(true).lower()
            //         //.attr("fill", "none")
            //         //.attr("stroke", "white")
            //         //.attr("stroke-width", 3)
            // )



        var link = link_group
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links, function(d){
                //console.log(d)
                //return d.id
                return Math.round(Math.random() * 10000000)
            })
            .join("line")
            .attr("stroke-width", 2)
            .attr("marker-end", "url(#arrows)");


        // var link2 = link_group
        //     .attr("stroke", "#999")
        //     .attr("fill", "none")
        //     .attr("stroke-opacity", 0.6)
        //     // .attr("stroke-linecap", strokeLinecap)
        //     // .attr("stroke-linejoin", strokeLinejoin)
        //     .attr("stroke-width", 2)
        //     .attr("marker-end", "url(#arrows)")
        //     .selectAll("path")
        //     .data(links, function(d){
        //         //console.log(d)
        //         //return d.id
        //         return Math.round(Math.random() * 10000000)
        //     })
        //     .join("path")
            
        //     .attr("d", 
        //         d3.linkHorizontal()
        //         .x(d => d.y)
        //         .y(d => d.x)
        //     );
            

        //     const link = svg.append("g")
        //     .attr("fill", "#999")
        //     .attr("stroke-width", 1.5)
        //   .selectAll("path")
        //   .data(links)
        //   .join("path")
        //     .attr("stroke", "#999")
        //     .attr("marker-end", "url(#arrows)");


            
        node.call(drag(simulation))
            
        node.append("circle")
            .attr("stroke", "white")
            .attr("stroke-width", 1.5)
            .attr("r", 10)
            .attr("fill", function(d){
                const scale = d3.scaleOrdinal(d3.schemeCategory10);
                return scale(d.group);
            });

        // node
        //     .append("rect")
        //     .attr("width", "300")
        //     .attr("height", "10")
        //     .attr("fill", "#ddd")
        //     .attr("style", "transform:translate(-10%, -5);")
        //     //.attr("stroke-width", "3")
        //     //.attr("stroke", "blue")

        node
            .append("text")
            .attr("text-anchor", "left")
            .attr("y", "-3.0em")
            .attr("font-weight", "bold")
            .text(d => d.theorem + " " + d.expression);
        
        node
            .append("text")
            .attr("text-anchor", "left")
            .attr("y", "-2.0em")
            .attr("font-size", "smaller")
            .text(d => "NormComp: " + d.norm_complexity);

        node
            .append("text")
            .attr("text-anchor", "left")
            .attr("y", "-1.0em")
            .attr("font-size", "smaller")
            .text(d => "LogComp: " + d.log_complexity);

        node
            .append("text")
            .attr("text-anchor", "left")
            .attr("y", "-0.0em")
            .attr("font-size", "smaller")
            .text(d => "EdgeCntNorm: " + d.edge_count_norm);
            

        // node.append("text")
        //     //.attr("x", 14)
        //     //.attr("y", "0.31em")
        //     .text(d => d.step + " - " + d.theorem + " " + d.expression)
        //     .text(d => d.theorem + " " + d.expression)
        //     .clone(true).lower()
        //     .attr("text-anchor", "middle")
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

      
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            // link2
            //     .attr("d", 
            //         d3.linkVertical()
            //             .x(d => d.x)
            //             .y(d => d.y)
            //     );



            node.attr("transform", d => `translate(${d.x},${d.y})`);
            // node
            //     .attr("cx", d => d.x)
            //     .attr("cy", d => d.y);
        });
      
        //invalidation.then(() => simulation.stop());


        //g.node();

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