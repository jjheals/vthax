export const basemaps = {
    OpenStreetNormal: {
        prettyName: 'Open Street Map',
        link: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '&copy; OpenStreetMap contributors'
    },
    EsriSatellite: {
        prettyName: 'Esri Satellite',
        link: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    },
    EsriStreetMap: {
        prettyName: 'Esri Street Map',
        link: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri'
    },
    EsriTopographic: {
        prettyName: 'Esri Topographic',
        link: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri'
    },
    CartoVoyager: {
        prettyName: 'Carto Voyager',
        link: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
        attribution: '&copy; OpenStreetMap contributors & Carto'
    },
    CartoLight: {
        prettyName: 'Carto Positron (light)',
        link: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        attribution: '&copy; OpenStreetMap contributors & Carto'
    },
    CartoDark: {
        prettyName: 'Carto Dark Matter (dark)',
        link: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        attribution: '&copy; OpenStreetMap contributors & Carto'
    }
}