from api.models import Property, Equipment

# Create Properties
properties_data = [
    {
        'title': 'Modern Downtown Loft',
        'description': 'Beautiful modern loft in the heart of downtown',
        'price': 1850,
        'location': 'Downtown, Manila',
        'bedrooms': 2,
        'bathrooms': 2,
        'area': 1200,
        'property_type': 'Apartment',
        'rating': 4.8,
        'image': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'
    },
    {
        'title': 'Luxury Penthouse Suite',
        'description': 'Stunning penthouse with amazing city views',
        'price': 3500,
        'location': 'Makati City',
        'bedrooms': 3,
        'bathrooms': 3,
        'area': 2400,
        'property_type': 'Penthouse',
        'rating': 4.9,
        'image': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'
    },
    {
        'title': 'Cozy Studio Apartment',
        'description': 'Perfect for singles or couples',
        'price': 1200,
        'location': 'Quezon City',
        'bedrooms': 1,
        'bathrooms': 1,
        'area': 650,
        'property_type': 'Studio',
        'rating': 4.5,
        'image': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'
    },
    {
        'title': 'Spacious Family Home',
        'description': 'Large family home with garden',
        'price': 2800,
        'location': 'Pasig City',
        'bedrooms': 4,
        'bathrooms': 3,
        'area': 2800,
        'property_type': 'House',
        'rating': 4.7,
        'image': 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800'
    }
]

# Create Equipment
equipment_data = [
    # Construction
    {'name': 'Excavator', 'category': 'construction', 'description': 'Heavy-duty excavator', 'price_per_day': 250, 'rating': 4.8, 'image': 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800', 'available': True},
    {'name': 'Concrete Mixer', 'category': 'construction', 'description': 'Industrial concrete mixer', 'price_per_day': 120, 'rating': 4.6, 'image': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800', 'available': True},
    {'name': 'Scaffolding Set', 'category': 'construction', 'description': 'Complete scaffolding system', 'price_per_day': 80, 'rating': 4.5, 'image': 'https://images.unsplash.com/photo-1590856029826-c7a73142bbf1?w=800', 'available': True},
    {'name': 'Power Generator', 'category': 'construction', 'description': '10KW power generator', 'price_per_day': 150, 'rating': 4.7, 'image': 'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800', 'available': True},
    {'name': 'Jackhammer', 'category': 'construction', 'description': 'Electric jackhammer', 'price_per_day': 90, 'rating': 4.4, 'image': 'https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?w=800', 'available': True},
    
    # Party & Event
    {'name': 'DJ Sound System', 'category': 'party', 'description': 'Professional DJ equipment', 'price_per_day': 150, 'rating': 4.9, 'image': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800', 'available': True},
    {'name': 'Party Tent 10x10', 'category': 'party', 'description': 'Large outdoor party tent', 'price_per_day': 200, 'rating': 4.7, 'image': 'https://images.unsplash.com/photo-1519167758481-83f29da8c2b0?w=800', 'available': True},
    {'name': 'LED Stage Lights', 'category': 'party', 'description': 'Professional stage lighting', 'price_per_day': 100, 'rating': 4.8, 'image': 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800', 'available': True},
    {'name': 'Karaoke Machine', 'category': 'party', 'description': 'Professional karaoke system', 'price_per_day': 80, 'rating': 4.6, 'image': 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=800', 'available': True},
    {'name': 'Folding Tables & Chairs', 'category': 'party', 'description': 'Set of 10 tables and 50 chairs', 'price_per_day': 120, 'rating': 4.5, 'image': 'https://images.unsplash.com/photo-1556911220-bff31c812dba?w=800', 'available': True},
    
    # Electronics
    {'name': 'Professional Camera', 'category': 'electronics', 'description': 'DSLR camera with lenses', 'price_per_day': 80, 'rating': 4.9, 'image': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800', 'available': True},
    {'name': 'Drone with 4K Camera', 'category': 'electronics', 'description': 'Professional drone', 'price_per_day': 120, 'rating': 4.8, 'image': 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800', 'available': True},
    {'name': 'Gaming Console PS5', 'category': 'electronics', 'description': 'PlayStation 5 with games', 'price_per_day': 50, 'rating': 4.7, 'image': 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=800', 'available': True},
    {'name': 'Projector & Screen', 'category': 'electronics', 'description': 'HD projector with screen', 'price_per_day': 70, 'rating': 4.6, 'image': 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800', 'available': True},
    {'name': 'Laptop MacBook Pro', 'category': 'electronics', 'description': 'High-performance laptop', 'price_per_day': 100, 'rating': 4.8, 'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800', 'available': True},
    
    # Vehicles
    {'name': 'Pickup Truck', 'category': 'vehicles', 'description': 'Toyota Hilux pickup', 'price_per_day': 120, 'rating': 4.7, 'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800', 'available': True},
    {'name': 'Van 12-Seater', 'category': 'vehicles', 'description': 'Spacious passenger van', 'price_per_day': 150, 'rating': 4.6, 'image': 'https://images.unsplash.com/photo-1527786356703-4b100091cd2c?w=800', 'available': True},
    {'name': 'Motorcycle', 'category': 'vehicles', 'description': 'Honda motorcycle', 'price_per_day': 60, 'rating': 4.5, 'image': 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=800', 'available': True},
    {'name': 'Bicycle Mountain Bike', 'category': 'vehicles', 'description': 'High-quality mountain bike', 'price_per_day': 30, 'rating': 4.4, 'image': 'https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800', 'available': True},
    {'name': 'Electric Scooter', 'category': 'vehicles', 'description': 'Electric scooter', 'price_per_day': 40, 'rating': 4.6, 'image': 'https://images.unsplash.com/photo-1559311042-f9b5e6c0f6f1?w=800', 'available': True},
    
    # Home & Garden
    {'name': 'Lawn Mower', 'category': 'home_garden', 'description': 'Gas-powered lawn mower', 'price_per_day': 45, 'rating': 4.5, 'image': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800', 'available': True},
    {'name': 'Pressure Washer', 'category': 'home_garden', 'description': 'High-pressure washer', 'price_per_day': 60, 'rating': 4.7, 'image': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800', 'available': True},
    {'name': 'Chainsaw', 'category': 'home_garden', 'description': 'Electric chainsaw', 'price_per_day': 50, 'rating': 4.6, 'image': 'https://images.unsplash.com/photo-1616430285228-8c4932a6e3e5?w=800', 'available': True},
    {'name': 'Leaf Blower', 'category': 'home_garden', 'description': 'Cordless leaf blower', 'price_per_day': 35, 'rating': 4.4, 'image': 'https://images.unsplash.com/photo-1615671524827-c1fe3973b648?w=800', 'available': True},
    {'name': 'Garden Tiller', 'category': 'home_garden', 'description': 'Rotary garden tiller', 'price_per_day': 55, 'rating': 4.5, 'image': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800', 'available': True},
]

print("Creating properties...")
for data in properties_data:
    Property.objects.create(**data)
print(f"Created {len(properties_data)} properties")

print("Creating equipment...")
for data in equipment_data:
    Equipment.objects.create(**data)
print(f"Created {len(equipment_data)} equipment items")

print("Database populated successfully!")
