# Project Skeleton for AI-Powered Chatbot

# === Backend (FastAPI + LangGraph) ===

from fastapi import FastAPI, HTTPException
from langchain import LangChain
from langchain.llms import HuggingFacePipeline
import databases
import sqlalchemy

# --- Database Setup ---
DATABASE_URL = "postgresql://user:password@localhost:5432/chatbot_db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("brand", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.Float),
    sqlalchemy.Column("category", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("supplier_id", sqlalchemy.Integer),
)

suppliers = sqlalchemy.Table(
    "suppliers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("contact_info", sqlalchemy.String),
    sqlalchemy.Column("product_categories", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

# --- FastAPI Setup ---
app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- Chatbot Endpoint ---
@app.post("/chatbot")
async def chatbot(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # LangChain Workflow Example
    llm = HuggingFacePipeline.from_pretrained("gpt-3.5-turbo")  # Replace with your chosen model
    workflow = LangChain(llm)

    # Example query handling
    if "products under brand" in query:
        brand = query.split("brand")[-1].strip()
        query_result = await database.fetch_all(query=products.select().where(products.c.brand == brand))
    elif "suppliers provide" in query:
        category = query.split("provide")[-1].strip()
        query_result = await database.fetch_all(query=suppliers.select().where(suppliers.c.product_categories.contains(category)))
    else:
        query_result = None

    if query_result:
        # Summarize with LLM
        structured_response = llm(f"Summarize the following data: {query_result}")
        return {"response": structured_response}

    return {"response": "No relevant data found."}

# === Frontend (React) ===
# Create a new React app (React + Tailwind CSS or Material UI for styling)
# Use Axios for API calls to the FastAPI backend
# Example React code will follow separately.

# === Database Population Script ===
import asyncio

async def populate_database():
    sample_products = [
        {"name": "Laptop X", "brand": "Brand X", "price": 1200.00, "category": "Electronics", "description": "High-performance laptop", "supplier_id": 1},
        {"name": "Smartphone Y", "brand": "Brand Y", "price": 800.00, "category": "Electronics", "description": "Latest model smartphone", "supplier_id": 2},
    ]
    sample_suppliers = [
        {"name": "Supplier A", "contact_info": "supplierA@example.com", "product_categories": "Electronics"},
        {"name": "Supplier B", "contact_info": "supplierB@example.com", "product_categories": "Furniture"},
    ]

    for product in sample_products:
        await database.execute(products.insert().values(**product))

    for supplier in sample_suppliers:
        await database.execute(suppliers.insert().values(**supplier))

# Run the population script
if __name__ == "__main__":
    asyncio.run(populate_database())
