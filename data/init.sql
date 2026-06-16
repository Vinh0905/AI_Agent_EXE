CREATE TABLE IF NOT EXISTS Warehouse (
    id_warehouse INT PRIMARY KEY AUTO_INCREMENT,
    id_owner INT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    description TEXT,
    location_address_text VARCHAR(255),
    location_province VARCHAR(100),
    location_commune VARCHAR(100),
    location_long DOUBLE,
    location_lat DOUBLE,
    location_postal_code VARCHAR(20),
    isSponsor BOOLEAN DEFAULT FALSE,
    sponsor_type INT,
    status VARCHAR(50),
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


INSERT INTO Warehouse
(id_warehouse, id_owner, name, address, description,
 location_address_text, location_province, location_commune,
 location_long, location_lat, location_postal_code,
 isSponsor, sponsor_type, status)
VALUES
(1, 1, 'Eimskip Bình Dương', 'KCN VSIP 1, Bình Dương',
 'Kho lạnh đông thực phẩm', 'Gần cổng chính VSIP 1',
 'Bình Dương', 'Thuận An',
 106.7050, 10.9050, '750000',
 TRUE, 1, 'Active'),

(2, 2, 'Mekong Cold Storage', 'KCN Tân Tạo, TP.HCM',
 'Kho lạnh bảo quản thủy sản', 'Khu công nghiệp Tân Tạo',
 'TP.HCM', 'Bình Tân',
 106.6025, 10.7897, '700000',
 FALSE, NULL, 'Active'),

(3, 3, 'Green Logistics Warehouse', 'KCN Amata, Đồng Nai',
 'Kho nhiệt độ phòng hàng tiêu dùng', 'Gần Quốc lộ 1A',
 'Đồng Nai', 'Biên Hòa',
 106.8854, 10.9539, '810000',
 TRUE, 2, 'Active'),

(4, 4, 'Central Storage Đà Nẵng', 'KCN Hòa Khánh, Đà Nẵng',
 'Kho mát dược phẩm', 'Trung tâm logistics miền Trung',
 'Đà Nẵng', 'Liên Chiểu',
 108.1520, 16.0740, '550000',
 FALSE, NULL, 'Active'),

(5, 5, 'Cần Thơ Logistics Hub', 'KCN Trà Nóc, Cần Thơ',
 'Kho đa năng nông sản xuất khẩu', 'Gần cảng Cần Thơ',
 'Cần Thơ', 'Bình Thủy',
 105.7645, 10.0452, '900000',
 TRUE, 3, 'Active');