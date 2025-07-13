# Appion API Documentation

## Address Management API

This API provides endpoints for managing Bangladesh's administrative divisions (Division → District → Upazila) with cascading dropdown support.

### Base URL
```
http://localhost:8000
```

---

## Address Endpoints

### 1. Get All Divisions
**GET** `/api/address/divisions`

Returns all divisions with their IDs.

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Chittagong"},
    {"id": 2, "name": "Rajshahi"},
    {"id": 3, "name": "Khulna"},
    {"id": 4, "name": "Barisal"},
    {"id": 5, "name": "Sylhet"},
    {"id": 6, "name": "Dhaka"},
    {"id": 7, "name": "Rangpur"},
    {"id": 8, "name": "Mymensingh"}
  ],
  "count": 8
}
```

---

### 2. Get Districts for Division
**GET** `/api/address/districts/{division_id}`

Returns all districts for a specific division.

**Parameters:**
- `division_id` (integer): ID of the division

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Chittagong"},
    {"id": 2, "name": "Comilla"},
    {"id": 3, "name": "Feni"},
    {"id": 4, "name": "Brahmanbaria"},
    {"id": 5, "name": "Chandpur"},
    {"id": 6, "name": "Lakshmipur"},
    {"id": 7, "name": "Cox's Bazar"},
    {"id": 8, "name": "Khagrachari"},
    {"id": 9, "name": "Rangamati"},
    {"id": 10, "name": "Noakhali"},
    {"id": 11, "name": "Bandarban"}
  ],
  "count": 11,
  "division": {"id": 1, "name": "Chittagong"}
}
```

**Error Response (404):**
```json
{
  "detail": "Division not found"
}
```

---

### 3. Get Upazilas for District
**GET** `/api/address/upazilas/{district_id}`

Returns all upazilas for a specific district.

**Parameters:**
- `district_id` (integer): ID of the district

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Rangunia"},
    {"id": 2, "name": "Sitakunda"},
    {"id": 3, "name": "Mirsharai"},
    {"id": 4, "name": "Patiya"},
    {"id": 5, "name": "Sandwip"},
    {"id": 6, "name": "Banshkhali"},
    {"id": 7, "name": "Boalkhali"},
    {"id": 8, "name": "Anwara"},
    {"id": 9, "name": "Chandanaish"},
    {"id": 10, "name": "Satkania"},
    {"id": 11, "name": "Lohagara"},
    {"id": 12, "name": "Hathazari"},
    {"id": 13, "name": "Fatikchhari"},
    {"id": 14, "name": "Raozan"},
    {"id": 15, "name": "Karnaphuli"},
    {"id": 16, "name": "Chittagong City Corporation"}
  ],
  "count": 16,
  "district": {"id": 1, "name": "Chittagong"}
}
```

**Error Response (404):**
```json
{
  "detail": "District not found"
}
```

---

### 4. Get Complete Address Hierarchy
**GET** `/api/address/hierarchy`

Returns the complete address hierarchy with all divisions, districts, and upazilas.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Chittagong",
      "districts": [
        {
          "id": 1,
          "name": "Chittagong",
          "upazilas": [
            {"id": 1, "name": "Rangunia"},
            {"id": 2, "name": "Sitakunda"},
            // ... more upazilas
          ]
        },
        // ... more districts
      ]
    },
    // ... more divisions
  ],
  "total_divisions": 8
}
```

---

### 5. Get Division Details
**GET** `/api/address/division/{division_id}`

Returns detailed information about a specific division with all its districts and upazilas.

**Parameters:**
- `division_id` (integer): ID of the division

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Chittagong",
    "districts": [
      {
        "id": 1,
        "name": "Chittagong",
        "upazilas": [
          {"id": 1, "name": "Rangunia"},
          {"id": 2, "name": "Sitakunda"},
          // ... more upazilas
        ]
      },
      // ... more districts
    ]
  }
}
```

---

## Frontend Implementation Guide

### Cascading Dropdown Implementation

Here's how to implement cascading dropdowns in your frontend:

#### 1. Load Divisions on Page Load
```javascript
// Load divisions when page loads
async function loadDivisions() {
  try {
    const response = await fetch('/api/address/divisions');
    const result = await response.json();
    
    if (result.success) {
      const divisionSelect = document.getElementById('division');
      divisionSelect.innerHTML = '<option value="">Select Division</option>';
      
      result.data.forEach(division => {
        const option = document.createElement('option');
        option.value = division.id;
        option.textContent = division.name;
        divisionSelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error('Error loading divisions:', error);
  }
}
```

#### 2. Load Districts When Division Changes
```javascript
// Load districts when division is selected
async function loadDistricts(divisionId) {
  try {
    const response = await fetch(`/api/address/districts/${divisionId}`);
    const result = await response.json();
    
    if (result.success) {
      const districtSelect = document.getElementById('district');
      districtSelect.innerHTML = '<option value="">Select District</option>';
      
      result.data.forEach(district => {
        const option = document.createElement('option');
        option.value = district.id;
        option.textContent = district.name;
        districtSelect.appendChild(option);
      });
      
      // Enable district select
      districtSelect.disabled = false;
      
      // Clear upazila select
      const upazilaSelect = document.getElementById('upazila');
      upazilaSelect.innerHTML = '<option value="">Select Upazila</option>';
      upazilaSelect.disabled = true;
    }
  } catch (error) {
    console.error('Error loading districts:', error);
  }
}
```

#### 3. Load Upazilas When District Changes
```javascript
// Load upazilas when district is selected
async function loadUpazilas(districtId) {
  try {
    const response = await fetch(`/api/address/upazilas/${districtId}`);
    const result = await response.json();
    
    if (result.success) {
      const upazilaSelect = document.getElementById('upazila');
      upazilaSelect.innerHTML = '<option value="">Select Upazila</option>';
      
      result.data.forEach(upazila => {
        const option = document.createElement('option');
        option.value = upazila.id;
        option.textContent = upazila.name;
        upazilaSelect.appendChild(option);
      });
      
      // Enable upazila select
      upazilaSelect.disabled = false;
    }
  } catch (error) {
    console.error('Error loading upazilas:', error);
  }
}
```

#### 4. Event Listeners
```javascript
// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
  loadDivisions();
  
  // Division change event
  document.getElementById('division').addEventListener('change', function() {
    if (this.value) {
      loadDistricts(this.value);
    } else {
      // Reset district and upazila selects
      document.getElementById('district').innerHTML = '<option value="">Select District</option>';
      document.getElementById('district').disabled = true;
      document.getElementById('upazila').innerHTML = '<option value="">Select Upazila</option>';
      document.getElementById('upazila').disabled = true;
    }
  });
  
  // District change event
  document.getElementById('district').addEventListener('change', function() {
    if (this.value) {
      loadUpazilas(this.value);
    } else {
      // Reset upazila select
      document.getElementById('upazila').innerHTML = '<option value="">Select Upazila</option>';
      document.getElementById('upazila').disabled = true;
    }
  });
});
```

### React Example

```jsx
import React, { useState, useEffect } from 'react';

function AddressSelector() {
  const [divisions, setDivisions] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [upazilas, setUpazilas] = useState([]);
  const [selectedDivision, setSelectedDivision] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedUpazila, setSelectedUpazila] = useState('');

  // Load divisions on component mount
  useEffect(() => {
    loadDivisions();
  }, []);

  const loadDivisions = async () => {
    try {
      const response = await fetch('/api/address/divisions');
      const result = await response.json();
      if (result.success) {
        setDivisions(result.data);
      }
    } catch (error) {
      console.error('Error loading divisions:', error);
    }
  };

  const loadDistricts = async (divisionId) => {
    try {
      const response = await fetch(`/api/address/districts/${divisionId}`);
      const result = await response.json();
      if (result.success) {
        setDistricts(result.data);
        setUpazilas([]);
        setSelectedDistrict('');
        setSelectedUpazila('');
      }
    } catch (error) {
      console.error('Error loading districts:', error);
    }
  };

  const loadUpazilas = async (districtId) => {
    try {
      const response = await fetch(`/api/address/upazilas/${districtId}`);
      const result = await response.json();
      if (result.success) {
        setUpazilas(result.data);
        setSelectedUpazila('');
      }
    } catch (error) {
      console.error('Error loading upazilas:', error);
    }
  };

  return (
    <div>
      <select 
        value={selectedDivision} 
        onChange={(e) => {
          setSelectedDivision(e.target.value);
          if (e.target.value) {
            loadDistricts(e.target.value);
          } else {
            setDistricts([]);
            setUpazilas([]);
          }
        }}
      >
        <option value="">Select Division</option>
        {divisions.map(division => (
          <option key={division.id} value={division.id}>
            {division.name}
          </option>
        ))}
      </select>

      <select 
        value={selectedDistrict} 
        onChange={(e) => {
          setSelectedDistrict(e.target.value);
          if (e.target.value) {
            loadUpazilas(e.target.value);
          } else {
            setUpazilas([]);
          }
        }}
        disabled={!selectedDivision}
      >
        <option value="">Select District</option>
        {districts.map(district => (
          <option key={district.id} value={district.id}>
            {district.name}
          </option>
        ))}
      </select>

      <select 
        value={selectedUpazila} 
        onChange={(e) => setSelectedUpazila(e.target.value)}
        disabled={!selectedDistrict}
      >
        <option value="">Select Upazila</option>
        {upazilas.map(upazila => (
          <option key={upazila.id} value={upazila.id}>
            {upazila.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default AddressSelector;
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- `200`: Success
- `404`: Resource not found
- `500`: Internal server error

---

## Testing the API

You can test the API using:

1. **FastAPI Interactive Docs**: Visit `http://localhost:8000/docs`
2. **cURL commands**:
   ```bash
   # Get all divisions
   curl http://localhost:8000/api/address/divisions
   
   # Get districts for division ID 1
   curl http://localhost:8000/api/address/districts/1
   
   # Get upazilas for district ID 1
   curl http://localhost:8000/api/address/upazilas/1
   ```

3. **Postman or similar API testing tools**

---

## Notes

- All addresses are now in English (no mapping required)
- The API automatically loads address data from `addresses.json` on startup
- All responses include a `success` flag for easy frontend handling
- Error responses include descriptive messages
- The hierarchy endpoint is useful for pre-loading all data if needed 