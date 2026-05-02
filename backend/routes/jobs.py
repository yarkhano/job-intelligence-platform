#This file contains all the URL endpoints that the frontend or anyone else
# can call to get job data. When someone visits /jobs in the browser the
#code in this file runs and returns job data as JSON.

from fastapi import APIRouter
from fastapi import Depends
from typing import List,Optional
from sqlalchemy.orm import session
from sqlalchemy import Text
from database import get_db
