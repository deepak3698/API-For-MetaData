import logging
from flask import Flask, request, jsonify
import json
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 

# Initializing app
app = Flask(__name__)
# Reading Data from Json
with open('config.json', 'r') as data:
    params = json.load(data)["params"]

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

# Initializing db
db = SQLAlchemy(app)

# Initializing ma
ma = Marshmallow(app)

# Location Class/Model
class Location(db.Model):
    location_id = db.Column(db.Integer,primary_key=True)    
    location_name = db.Column(db.String(100), nullable=False)
    location_desc = db.Column(db.Integer, nullable=False)

# Location Schema
class LocationSchema(ma.Schema):
    class Meta:
        fields = ('location_id', 'location_name','location_desc')

# Department Class/Model
class Department(db.Model):
    department_id = db.Column(db.Integer,primary_key=True)    
    department_name = db.Column(db.String(100), nullable=False)
    department_desc = db.Column(db.Integer, nullable=False)
    location_id = db.Column(db.Integer,nullable=False)

# Department Schema
class DepartmentSchema(ma.Schema):
    class Meta:
        fields = ('department_id', 'department_name','department_desc','location_id')

# Category Class/Model
class Category(db.Model):
    category_id = db.Column(db.Integer,primary_key=True)    
    category_name = db.Column(db.String(100), nullable=False)
    category_desc = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer,nullable=False)

    
# Category Schema
class CategorySchema(ma.Schema):
    class Meta:
        fields = ('category_id', 'category_name','category_desc','department_id')

# SubCategory Class/Model
class Subcategory(db.Model):
    subcategory_id = db.Column(db.Integer,primary_key=True)    
    subcategory_name = db.Column(db.String(100), nullable=False)
    subcategory_desc = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer,nullable=False)

    
# Subcategory Schema
class SubcategorySchema(ma.Schema):
    class Meta:
        fields = ('subcategory_id', 'subcategory_name','subcategory_desc','category_id')

# Initializing schema for location
locations_schema = LocationSchema(many=True)

# Initializing schema for Department
department_schema = DepartmentSchema(many=True)

# Initializing schema for Category
category_schema = CategorySchema(many=True)

#Creating app route for GET request
@app.route('/<string:location>', methods=['GET'])
@app.route('/<string:location>/<int:location_id>', methods=['GET'])
@app.route('/<string:location>/<int:location_id>/<string:department>',methods=['GET'])
@app.route('/<string:location>/<int:location_id>/<string:department>/<int:department_id>', methods=['GET'])
@app.route('/<string:location>/<int:location_id>/<string:department>/<int:department_id>/<string:category>', methods=['GET'])
def getData(location="",location_id=0,department="",department_id=0,category=""):
    try:
        if location=="location":   
            if location_id==0:
                locations = Location.query.all()
                res=locations_schema.dump(locations)
                return jsonify(res),200
            else:
                if department=="":
                    location_data=Location.query.filter_by(location_id=location_id).all()
                    res=locations_schema.dump(location_data)
                    return jsonify(res),200
                else:
                    if department=="department":
                        if department_id==0:
                            department=Department.query.filter_by(location_id=location_id).all()
                            res=department_schema.dump(department)
                            return jsonify(res),200
                        else:
                            if category=="":
                                department_date=Department.query.filter_by(department_id=department_id,location_id=location_id).all()
                                res=department_schema.dump(department_date)
                                return jsonify(res),200
                            else:
                                if category=="category":
                                    category_data=Category.query.filter_by(department_id=department_id).all()
                                    res=category_schema.dump(category_data)
                                    return jsonify(res),200
                                else:
                                    logging.info("category path is not correct")
                                    return jsonify({"error":"400 bad request"}),400                
                    else:
                        logging.info("department path is not correct")
                        return jsonify({"error":"400 bad request"}),400
        else:
            logging.info("location path is not correct")
            return jsonify({"error":"400 bad request"}),400
    except Exception as error:
        logging.error(error)
        return jsonify({"error":"Something went wrong in db"}),500
    
@app.route('/<string:post_request_name>', methods=['POST'])
def addData(post_request_name):
    try:
        post_request_data=request.get_data()
        post_request_data=json.loads(post_request_data)
    except:
        logging.error("Error in parsing data")
        return jsonify({"error":"error in parsing data"}),400
    try:
        if post_request_name=='location':
            new_location=Location(location_id=post_request_data["location_id"],location_name=post_request_data["location_name"],location_desc=post_request_data["location_desc"])
            db.session.add(new_location)
            db.session.commit()
            return jsonify({"Success":"Successfully added the record"}),200

        elif post_request_name=='department':
            new_department=Department(department_id=post_request_data["department_id"],department_name=post_request_data["department_name"],department_desc=post_request_data["department_desc"],location_id=post_request_data["location_id"])
            db.session.add(new_department)
            db.session.commit()
            return jsonify({"Success":"Successfully added the record"}),200

        elif post_request_name=='category':
            new_category=Category(category_id=post_request_data["category_id"],category_name=post_request_data["category_name"],category_desc=post_request_data["category_desc"],department_id=post_request_data["department_id"])
            db.session.add(new_category)
            db.session.commit()
            return jsonify({"Success":"Successfully added the record"}),200

        elif post_request_name=='subcategory':
            new_subcategory=Subcategory(subcategory_id=post_request_data["subcategory_id"],subcategory_name=post_request_data["subcategory_name"],subcategory_desc=post_request_data["subcategory_desc"],category_id=post_request_data["category_id"])
            db.session.add(new_subcategory)
            db.session.commit()
            return jsonify({"Success":"Successfully added the record"}),200

        else:
            logging.info("post_request_name path is not correct")
            return jsonify({"error":"400 bad request"}),400
    except Exception as error:
        logging.info(error)
        return jsonify({"Error":"Something went wrong in db"}),500

    
@app.route('/<string:post_request_name>/<int:post_req_id>', methods=['PUT','DELETE'])
def Update_delete_data(post_request_name,post_req_id):
    if request.method=='PUT':
        try:
            post_request_data=request.get_data()
            post_request_data=json.loads(post_request_data)
        except:
            logging.error("post_request_name path is not correct")
            return jsonify({"Error":"error in parsing data"}),400
        try:
            if post_request_name=='location':
                location = Location.query.get(post_req_id)
                location.location_name=post_request_data["location_name"]
                location.location_name=post_request_data["location_desc"]
                db.session.commit()
                return jsonify({"Success":"Successfully updated the record"}),200

            elif post_request_name=='department':
                department = Department.query.get(post_req_id)
                department.department_name=post_request_data["department_name"]
                department.department_desc=post_request_data["department_desc"]
                db.session.commit()
                return jsonify({"Success":"Successfully updated the record"}),200

            elif post_request_name=='category':
                category = Category.query.get(post_req_id)
                category.category_name=post_request_data["category_name"]
                category.category_desc=post_request_data["category_desc"]
                db.session.commit()
                return jsonify({"Success":"Successfully updated the record"}),200

            elif post_request_name=='subcategory':
                subcategory = Subcategory.query.get(post_req_id)
                subcategory.subcategory_name=post_request_data["subcategory_name"]
                subcategory.subcategory_desc=post_request_data["subcategory_desc"]
                db.session.commit()
                return jsonify({"Success":"Successfully updated the record"}),200

            else:
                logging.info("post_request_name path is not correct")
                return jsonify({"error":"400 bad request"}),400
        except Exception as error:
            logging.info(error)
            return jsonify({"Error":"Something went wrong in DB"}),500

    if request.method=='DELETE':
        try:
            if post_request_name=='location':
                location = Location.query.get(post_req_id)
                db.session.delete(location)
                db.session.commit()
                return jsonify({"Success": "Deleted successfully"}),200

            elif post_request_name=='department':
                department = Department.query.get(post_req_id)
                db.session.delete(department)
                db.session.commit()
                return jsonify({"Success": "Deleted successfully"}),200

            elif post_request_name=='category':
                category = Category.query.get(post_req_id)
                db.session.delete(category)
                db.session.commit()
                return jsonify({"Success": "Deleted successfully"}),200

            elif post_request_name=='subcategory':
                subcategory = Subcategory.query.get(post_req_id)
                db.session.delete(subcategory)
                db.session.commit()
                return jsonify({"Success": "Deleted successfully"}),200

            else:
                logging.info("post_request_name path is not correct")
                return jsonify({"error":"400 bad request"}),400
        except Exception as error:
            logging.info(error)
            return jsonify({"error":"Something went wrong in DB"}),500

# Run Server
if __name__ == '__main__':
    app.run()