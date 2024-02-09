# ดาวน์โหลดแผนที่
# folium module (openstreetmap)
import folium

# สร้างแผนที่
thailand_map = folium.Map(location=[13.7563, 100.5018], zoom_start=6)

# เพิ่มเครื่องหมายบนแผนที่
folium.Marker([13.7563, 100.5018], popup='Bangkok').add_to(thailand_map)
folium.Marker([18.7682, 98.9747], popup='Chiang Mai').add_to(thailand_map)
folium.Marker([15.22806, 104.85944], popup='Ubonratchatani').add_to(thailand_map)
folium.Marker([7.55750, 99.61028],popup='Trang').add_to(thailand_map)

folium.PolyLine(locations=[[13.7563, 100.5018], [18.7682, 98.9747], [15.22806, 104.85944], [7.55750, 99.61028]], color='blue').add_to(thailand_map)

# แสดงแผนที่
thailand_map.save('thailand_map.html')  # บันทึกแผนที่เป็นไฟล์ HTML

