"use strict";
 
function main(){
	// create the map using the travelMap ID tag. Set the (lat, lon) render-centre, and initial zoom level
	let map = L.map("map", {
		center: [-37.87, 175.475], 
		zoom: 12
        });
        	
	// get tiles from openstreetmap.org, add attribution etc. Add tiles to map.
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 18,
			subdomains: ['a','b','c']
			}).addTo(map);
    
	// add markers to map, from places.json. 
	// for ( let i=0; i < markers.length; i++ ) {
	// 	L.marker( [markers[i].lat, markers[i].lng] )
	// 		// set the popup text to be the city and country that the marker refers to
	// 		.bindPopup( markers[i].city + ", " + markers[i].country )
	// 		.addTo( map );
    // }
    
    let heat = L.heatLayer([
        [-37.90295525,175.4772238333,0.331566754675031],
        [-37.9155634,175.47150915,0.0330886810539454],
        [-37.9077980667,175.4749606833,0.0553410958886463],
        [-37.9024718333,175.47689145,0.555126115173718],
        [-37.9010265333,175.4781286667,0.846069812688032],
        [-37.9051546167,175.4761810167,0.0892525576065953],
        [-37.9027743667,175.4772973,0.825905559386503],
        [-37.9113692333,175.4732625,0.382826719439399],
        [-37.9061175,175.4761095667,0.0675455473384583],
        [-37.9126536833,175.4718492,0.590075732442714],
        [-37.89984655,175.47884775,0.96350573450757],
        [-37.8996625,175.4783593833,0.0212573374476552],
        [-37.9096838,175.4734820333,0.15434154031539],
        [-37.9163971333,175.4703382333,0.655546251121835],
        [-37.9019659333,175.47801565,0.495373866646281],
        [-37.9017677,175.4778972667,0.545913378087492],
        [-37.9082934833,175.4747193,0.668460695656423],
        [-37.9124935167,175.4721662833,0.802100320556479],
        [-37.9112822667,175.4727057,0.633489041919876],
        [-37.9088314833,175.4744561333,0.62742638749223],
        [-37.9140193667,175.4723065,0.766882008309998],
        [-37.9151048833,175.4715047667,0.266503161072438],
        [-37.9155721667,175.4712705333,0.488621588652691],
        [-37.91564375,175.4698925833,0.970506803458753],
        [-37.9157315333,175.4712060333,0.276762853991245],
        [-37.9158956833,175.4711298667,0.761584090132723],
        [-37.9044821667,175.4765082167,0.17487089909492],
        [-37.9045073333,175.4759204333,0.1891805552013],
        [-37.9046759167,175.4758561667,0.893369510759159],
        [-37.8983034667,175.4792230333,0.560477608746508],
        [-37.8987899833,175.4796567167,0.330237470617188]        
    ], {radius: 25}).addTo(map);
	
	// Get the unique countries visited (don't actually do anything with them; just for interest...!)
	let countriesVisited = []; 
	markers.forEach( function(d) { countriesVisited.push(d.country); });
	let uniqueCountries = new Set(countriesVisited);
	console.log(uniqueCountries);
}

// run the script
main();