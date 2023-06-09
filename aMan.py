from database import DatabaseHandler
from pathlib import Path
import re
import os

class User:
    username: str
    user_id: int
    nameFirst: str
    nameLast: str
    email: str

    def __init__(self) -> None:
        self.database_file = f"{os.environ['AMAN']}"

        self.username = os.getlogin()
        self.user_id = self.get_user_id()

    def get_user_id(self) -> int:
        """Looks for a matching username in users table and returns the user_id value

        Returns:
            int: user_id
        """
        query = "SELECT user_id FROM users WHERE username = %s;"
        params = (self.username,)
        with DatabaseHandler(self.database_file) as db:
            result = db.fetch_data(query, params)
            if result:
                return result[0][0]
            else:
                return None
    
    def create_user(self, nameFirst="", nameLast="", email=""):
        """Creates a new user in the users table. Updates it's properties with the result.

        Args:
            nameFirst (str): _description_
            nameLast (str): _description_
            email (str): _description_
        """
        query = "INSERT INTO users(username, nameFirst, nameLast, email) VALUES(%s, %s, %s, %s);"
        params = (self.username, nameFirst, nameLast, email,)
        with DatabaseHandler(self.database_file) as db:
            db.execute_query(query, params)
            user_id = db.get_last_insert_id()
            query = "SELECT * FROM users WHERE user_id = %s"
            params = (user_id,)
            user = db.fetch_data(query, params)[0]
            self.user_id = user[0]
            self.nameFirst = user[1]
            self.nameLast = user[2]
            self.email = user[3]

class aMan:
    def __init__(self):
        self.database_file = f"{os.environ['AMAN']}"
        self.user = None

    def set_user(self, user: User):
        self.user = user

    def get_assets(self) -> list:
        """Returns all assets in DATABASE.assets in ascending order by asset_id

        Returns:
            list: (asset_id, asset_name, asset_path, asset_type,)
        """
        query = "SELECT * FROM assets ORDER BY asset_id ASC"
        with DatabaseHandler(self.database_file) as db:
            return db.fetch_data(query)
    
    def get_changelog(self, asset_id: int) -> list:
        """Returns all changelog entries for a given asset, asset_id

        Args:
            asset_id (int): A valid primary key from DATABASE.assets

        Returns:
            list: (chlog_timestamp, chlog_message, username,)
        """
        query = "SELECT chlog_timestamp, chlog_message, username FROM changelog c JOIN users u on c.user_id = u.user_id WHERE asset_id = %s"

        params = (asset_id,)
        with DatabaseHandler(self.database_file) as db:
            return db.fetch_data(query, params)
    
    def get_versions(self, asset_id: int) -> list:
        """Returns all versions for a given asset, asset_id

        Args:
            asset_id (int): A valid primary key from DATABASE.assets

        Returns:
            list: (asset_version, version_path,)
        """
        query = "SELECT asset_version, version_path FROM asset_production WHERE asset_id = %s"
        params = (asset_id,)
        with DatabaseHandler(self.database_file) as db:
            return db.fetch_data(query, params)
    
    def log_change(self, asset_id: int, message: str):
        """Insert a changelog entry for the given asset.  The username will automatically be added to the entry

        Args:
            asset_id (int): A valid primary key from DATABASE.assets
            message (str): A brief description of what was changed with this asset
        """
        query = "INSERT INTO changelog(asset_id, chlog_message, user_id) VALUES(%s, %s, %s)"
        params = (asset_id, message, self.user.user_id)
        with DatabaseHandler(self.database_file) as db:
            db.execute_query(query, params)

    def create_asset(self, asset_name: str, asset_type: str, asset_path: str):
        """Inserts a new row into the assets table, captures the autoincremented asset_id, then creates a changelog entry

        Args:
            asset_name (str): Name of the asset
            asset_type (str): The type of asset, ie. Maya (.ma, .mb), Geo (.obj, .fbx, .abc), Img (.jpg, .png, .tiff)
            asset_path (str): A valid path to an existing file on disk.
        """
        if not Path(asset_path).exists():
            return
        
        query = "INSERT INTO assets(asset_name, asset_path, asset_type) VALUES(%s, %s, %s);"
        params = (asset_name, asset_path, asset_type)
        with DatabaseHandler(self.database_file) as db:
            error_code = db.execute_query(query, params)
            if error_code == 0:
                asset_id = db.get_last_insert_id()
                message = "Asset Created"
                self.log_change(asset_id, message)
                print(f"Successfull created asset:\n\tID: {asset_id}\n\tAsset Name: {asset_name}\n\tAsset Type: {asset_type}\n\tAsset Path: {asset_path}")
                return asset_id
            else:
                if error_code == 1062:
                    # Duplicate Error, return the existing asset id
                    query = "SELECT * FROM assets WHERE asset_path = %s;"
                    params = (asset_path,)
                    asset_id, asset_name, asset_path, asset_type = db.fetch_data(query, params)[0]
                    print(f"Asset already exists:\n\tID: {asset_id}\n\tAsset Name: {asset_name}\n\tAsset Type: {asset_type}\n\tAsset Path: {asset_path}")
                    return asset_id


    def delete_asset(self, asset_id: int) -> bool:
        """Deletes a asset from the database.  All related changelog entries will also be deleted

        Args:
            asset_id (int): A valid primary key from DATABASE.assets

        Returns:
            bool: Successful Deletion
        """
        query = "DELETE FROM assets WHERE asset_id = %s"
        params = (asset_id,)
        with DatabaseHandler(self.database_file) as db:
            db.execute_query(query, params)
            if db.cur.rowcount > 0:
                print(f"Asset: {asset_id} successfully deleted")
                return True
            else:
                print(f"Asset: {asset_id} failed to delete")
                return False

    def version_asset(self, asset_id: int, version: int, version_path: str, message=""):
        query = "INSERT INTO asset_production(asset_id, asset_version, version_path) VALUES(%s, %s, %s);"
        params = (asset_id, version, version_path)
        with DatabaseHandler(self.database_file) as db:
            db.execute_query(query, params)
            if message == "": message = f"Versioned asset to {asset_id}"
            self.log_change(asset_id, message)

