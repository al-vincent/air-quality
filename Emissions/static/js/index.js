"use strict";

// lat, lng, intensity for different types of emissions
const EMISSION_TYPES = [
    {"lat":-37.90295525,"lng":175.4772238333,"carbon-monoxide":0.331566754675031,"nitrogen-dioxide":1},
    {"lat":-37.9155634,"lng":175.47150915,"carbon-monoxide":0.0553410958886463,"nitrogen-dioxide":1},
    {"lat":-37.9077980667,"lng":175.4749606833,"carbon-monoxide":0.0892525576065953,"nitrogen-dioxide":1},
    {"lat":-37.9024718333,"lng":175.47689145,"carbon-monoxide":0.590075732442714,"nitrogen-dioxide":1},
    {"lat":-37.9010265333,"lng":175.4781286667,"carbon-monoxide":0.15434154031539,"nitrogen-dioxide":1},
    {"lat":-37.9051546167,"lng":175.4761810167,"carbon-monoxide":0.545913378087492,"nitrogen-dioxide":1},
    {"lat":-37.9027743667,"lng":175.4772973,"carbon-monoxide":0.633489041919876,"nitrogen-dioxide":1},
    {"lat":-37.9113692333,"lng":175.4732625,"carbon-monoxide":0.266503161072438,"nitrogen-dioxide":1},
    {"lat":-37.9061175,"lng":175.4761095667,"carbon-monoxide":0.276762853991245,"nitrogen-dioxide":1},
    {"lat":-37.9126536833,"lng":175.4718492,"carbon-monoxide":0.1891805552013,"nitrogen-dioxide":1},
    {"lat":-37.89984655,"lng":175.47884775,"carbon-monoxide":0.0675455473384583,"nitrogen-dioxide":1},
    {"lat":-37.8996625,"lng":175.4783593833,"carbon-monoxide":0.0330886810539454,"nitrogen-dioxide":1},
    {"lat":-37.9096838,"lng":175.4734820333,"carbon-monoxide":0.555126115173718,"nitrogen-dioxide":1},
    {"lat":-37.9163971333,"lng":175.4703382333,"carbon-monoxide":0.825905559386503,"nitrogen-dioxide":1},
    {"lat":-37.9019659333,"lng":175.47801565,"carbon-monoxide":0.96350573450757,"nitrogen-dioxide":1},
    {"lat":-37.9017677,"lng":175.4778972667,"carbon-monoxide":0.655546251121835,"nitrogen-dioxide":1},
    {"lat":-37.9082934833,"lng":175.4747193,"carbon-monoxide":0.668460695656423,"nitrogen-dioxide":1},
    {"lat":-37.9124935167,"lng":175.4721662833,"carbon-monoxide":0.62742638749223,"nitrogen-dioxide":1},
    {"lat":-37.9112822667,"lng":175.4727057,"carbon-monoxide":0.488621588652691,"nitrogen-dioxide":1},
    {"lat":-37.9088314833,"lng":175.4744561333,"carbon-monoxide":0.761584090132723,"nitrogen-dioxide":1},
    {"lat":-37.9140193667,"lng":175.4723065,"carbon-monoxide":0.893369510759159,"nitrogen-dioxide":1},
    {"lat":-37.9151048833,"lng":175.4715047667,"carbon-monoxide":0.330237470617188,"nitrogen-dioxide":1},
    {"lat":-37.9155721667,"lng":175.4712705333,"carbon-monoxide":0.846069812688032,"nitrogen-dioxide":1},
    {"lat":-37.91564375,"lng":175.4698925833,"carbon-monoxide":0.382826719439399,"nitrogen-dioxide":1},
    {"lat":-37.9157315333,"lng":175.4712060333,"carbon-monoxide":0.0212573374476552,"nitrogen-dioxide":1},
    {"lat":-37.9158956833,"lng":175.4711298667,"carbon-monoxide":0.495373866646281,"nitrogen-dioxide":1},
    {"lat":-37.9044821667,"lng":175.4765082167,"carbon-monoxide":0.802100320556479,"nitrogen-dioxide":1},
    {"lat":-37.9045073333,"lng":175.4759204333,"carbon-monoxide":0.766882008309998,"nitrogen-dioxide":1},
    {"lat":-37.9046759167,"lng":175.4758561667,"carbon-monoxide":0.970506803458753,"nitrogen-dioxide":1},
    {"lat":-37.8983034667,"lng":175.4792230333,"carbon-monoxide":0.17487089909492,"nitrogen-dioxide":1},
    {"lat":-37.8987899833,"lng":175.4796567167,"carbon-monoxide":0.560477608746508,"nitrogen-dioxide":1}
]

const DEFAULT_EMISSIONS = "carbon-monoxide";
const DEFAULT_ILLNESS = "asthma";

function getEmissionsValues(emissionsType){
    return EMISSION_TYPES.map( function(elem) {        
        return [elem["lat"], elem["lng"], elem[emissionsType]];
    });
}

function main(){
	// create the map using the travelMap ID tag. Set the (lat, lon) render-centre, and initial zoom level
	let map = L.map("map", {
		center: [-37.9, 175.475], 
		zoom: 16
        });

    let heat = null;
        	
	// get tiles from openstreetmap.org, add attribution etc. Add tiles to map.
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 18,
			subdomains: ['a','b','c']
			}).addTo(map);
    
    // add a series of points ot the map, with randomly-generated intensities
    // console.log(getEmissionsValues(DEFAULT_EMISSIONS));
    heat = L.heatLayer(getEmissionsValues(DEFAULT_EMISSIONS), 
                            {radius: 15, blur: 5}).addTo(map); 
    console.log(heat);
    
    const emissionsList = document.getElementById('list-emissions');
    emissionsList.addEventListener("change", function(){
        const newEmissionsType = document.getElementById('list-emissions').value;
        // get the new intensities (need to check via console!)
        const newEmissions = getEmissionsValues(newEmissionsType);
        // remove the existing points from the map
        heat.remove();
        // plot the new points
        heat = L.heatLayer(newEmissions, {radius: 15, blur: 5}).addTo(map);
        console.log(heat);
        console.log("map updated");
    });
}

// run the script
main();