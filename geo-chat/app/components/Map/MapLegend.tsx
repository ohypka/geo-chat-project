import L from "leaflet";
import {useMap} from "react-leaflet";
import {useEffect} from "react";
import {LEGENDS} from "../../data/legendData";

interface MapLegendProps {
    type: string;
}

export default function MapLegend({type}:MapLegendProps){
    const map = useMap();

    useEffect(()=>{
        const info=new L.Control({position:"bottomright"})
        if (!type || !(type in LEGENDS)) return;

        const legendKey = type as keyof typeof LEGENDS;

        info.onAdd=function(){
            const div=L.DomUtil.create("div");
            const { title, items } = LEGENDS[legendKey];

            div.innerHTML = `
                <div style="
                    background:black;
                    padding:10px;
                    border-radius:8px;
                    box-shadow:0 0 10px rgba(0,0,0,0.3);
                    font-size:14px;
                ">
                    <strong>${title}</strong>
                    ${items.map(i => `
                        <div style="display:flex;align-items:center;margin-top:6px;">
                            <span style="
                                width:14px;
                                height:14px;
                                border-radius:50%;
                                background:${i.color};
                                display:inline-block;
                                margin-right:6px;
                            "></span>
                            ${i.label}
                        </div>
                    `).join("")}
                </div>
            `;
            return div;
        }
        info.addTo(map);

        return () => {
            info.remove();
        };

    },[map,type]);
    return null;
}