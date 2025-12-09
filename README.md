# Laboratory Chemical Management System

A comprehensive web-based system for managing laboratory chemicals, inventory, and safety information.

## Features

- Chemical inventory management
- Add, edit, delete, and search chemicals
- Track chemical quantities and locations
- Safety information and hazard warnings
- Storage location tracking
- Expiration date monitoring
- User-friendly web interface

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **UI/UX Design**: Based on Figma design specifications

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Malith200203/Chemical-manegment-systerm.git
cd Chemical-manegment-systerm
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install required packages:
```bash
pip install -r requirements.txt
```

5. Initialize the database:
```bash
python init_db.py
```

## Running the Application

1. Make sure your virtual environment is activated

2. Start the Flask server:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Database Schema

The application uses the following main tables:

- **chemicals**: Stores chemical information (name, formula, CAS number, etc.)
- **inventory**: Tracks chemical quantities and locations
- **storage_locations**: Manages storage areas in the laboratory
- **hazard_categories**: Defines safety hazard classifications
- **users**: Manages user accounts and permissions

## Usage

1. **Dashboard**: View overview of inventory and recent activities
2. **Add Chemical**: Register new chemicals in the system
3. **View Inventory**: Browse and search existing chemicals
4. **Update Quantity**: Adjust chemical quantities
5. **Safety Info**: Access hazard and safety data

## Project Structure

```
Chemical-manegment-systerm/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── database.py           # Database models and operations
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/            # HTML templates
│   ├── index.html
│   ├── add_chemical.html
│   ├── inventory.html
│   └── chemical_detail.html
└── README.md
```

## API Endpoints

- `GET /` - Home page
- `GET /api/chemicals` - Get all chemicals
- `POST /api/chemicals` - Add new chemical
- `GET /api/chemicals/<id>` - Get chemical details
- `PUT /api/chemicals/<id>` - Update chemical
- `DELETE /api/chemicals/<id>` - Delete chemical
- `GET /api/inventory` - Get inventory status
- `GET /api/locations` - Get storage locations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

## Design Reference

UI/UX Design: [Figma Link](https://www.figma.com/design/9B8a4VrWxzegqoAikuC8zT/Untitled?node-id=0-1&p=f&t=nERx1bvhkTlMjAFw-0)
