"""
@file-overview Routes and API endpoints for the Document AI Analysis service
@filepath routes.py

This module handles all the HTTP routes for the document analysis application.
It provides endpoints for:
- File upload and validation
- Document processing and analysis
- Payment processing via Stripe
- Serving the main application interface

The module integrates with:
- Document processing utilities
- AI analysis service
- Stripe payment processing
- Database models for documents and payments
"""

import os
import uuid
from typing import Tuple, Dict, Any
from datetime import datetime
from flask import render_template, request, jsonify, Response
from werkzeug.datastructures import FileStorage
from app import app, db
from models import Document, Payment
from utils.document_processor import process_document
from utils.ai_analyzer import analyze_document
from utils.stripe_utils import (
    create_payment_intent,
    confirm_payment_intent,
)

# define allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx"}

# define upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Pricing tiers in Chinese Yuan (CNY), stored in cents
PRICING_TIERS = [
    {"max_chars": 1000, "price": 100},  # ¥1.00 for <= 1000 chars
    {"max_chars": 5000, "price": 200},  # ¥2.00 for <= 5000 chars
    {"max_chars": 10000, "price": 300},  # ¥3.00 for <= 10000 chars
    {"max_chars": 50000, "price": 500},  # ¥5.00 for <= 50000 chars
    {"max_chars": 100000, "price": 800},  # ¥8.00 for <= 100000 chars
    {"max_chars": float("inf"), "price": 1000},  # ¥10.00 for > 100000 chars
]


def _allowed_file(filename: str) -> bool:
    """
    Check if the file extension is allowed.

    Args:
        filename: Name of the file to check

    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    allowed_extensions = app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def _generate_unique_filename(original_filename: str) -> Tuple[str, str]:
    """
    Generate a unique filename while preserving the original extension.

    Args:
        original_filename: Original name of the uploaded file

    Returns:
        Tuple[str, str]: Tuple containing (unique_filename, file_extension)
    """
    original_filename_without_extension = original_filename.rsplit(".", 1)[0]
    file_extension = (
        original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else ""
    )
    unique_filename = (
        f"{original_filename_without_extension}_{uuid.uuid4().hex}.{file_extension}"
    )
    return unique_filename, file_extension


def _save_uploaded_file(file: FileStorage, save_path: str) -> None:
    """
    Save the uploaded file to the specified path.

    Args:
        file: The uploaded file object
        save_path: Path where the file should be saved

    Raises:
        OSError: If file cannot be saved
    """
    try:
        file.save(save_path)
        app.logger.info(f"✅ File saved successfully at {save_path}")
    except Exception as e:
        app.logger.error(f"⚠️ Failed to save file: {str(e)}")
        raise OSError(f"Failed to save file: {str(e)}")


def _calculate_analysis_cost(char_count: int) -> int:
    """
    Calculate the analysis cost based on character count.
    Ensures minimum charge meets Stripe's requirement of 50 cents USD.

    Args:
        char_count: Number of characters in the document

    Returns:
        int: Cost in cents (¥)
    """
    pricing_tiers = app.config["PRICING_TIERS"]
    min_charge = app.config["MIN_CHARGE"]

    # Base cost calculation
    cost = next(
        (tier["price"] for tier in pricing_tiers if char_count <= tier["max_chars"]),
        min_charge,
    )

    # Ensure minimum charge meets Stripe's requirement
    return max(cost, min_charge)


def _process_payment(amount: int, currency: str = "cny") -> Dict[str, Any]:
    """
    Create a payment intent for document analysis.

    Args:
        amount: Amount to charge in cents
        currency: Currency code (default: "cny")

    Returns:
        Dict containing payment intent details
    """
    payment_intent = create_payment_intent(amount, currency=currency)
    return {
        "client_secret": payment_intent.client_secret,
        "publishable_key": app.config["STRIPE_PUBLISHABLE_KEY"],
        "amount": amount,
        "currency": currency,
    }


@app.route("/")
def index() -> str:
    """Render the main application page."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file() -> Tuple[Response, int]:
    """
    Handle file upload, process document, and create payment intent.

    Returns:
        Tuple[Response, int]: JSON response and HTTP status code
    """
    save_path = None
    try:
        # 1. File validation
        if "file" not in request.files:
            app.logger.error("🚫 No file part in the request")
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            app.logger.error("🚫 No file selected")
            return jsonify({"error": "No file selected"}), 400

        if not _allowed_file(file.filename):
            app.logger.error(f"🚫 Invalid file type: {file.filename}")
            return jsonify({"error": "Invalid file type. Only PDF and DOCX files are allowed"}), 400

        # 2. Save file with cleanup on failure
        try:
            unique_filename, _ = _generate_unique_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            _save_uploaded_file(file, save_path)
        except OSError as e:
            app.logger.error(f"⚠️ File save error: {str(e)}")
            return jsonify({"error": "Failed to save file"}), 500

        # 3. Process document and calculate cost
        try:
            document_metadata = process_document(save_path)
            char_count = document_metadata["char_count"]
            analysis_cost = _calculate_analysis_cost(char_count)
            app.logger.info(f"💰 Analysis cost: ¥{analysis_cost / 100:.2f} for {char_count} characters")
        except Exception as e:
            if save_path and os.path.exists(save_path):
                os.remove(save_path)
            app.logger.error(f"⚠️ Processing error: {str(e)}")
            return jsonify({"error": "Document processing failed"}), 500

        # 4. Database entry
        try:
            document = Document(
                filename=unique_filename,
                original_filename=file.filename,
                file_size=os.path.getsize(save_path),
                mime_type=file.content_type,
                char_count=char_count,
                analysis_cost=analysis_cost,
                title=document_metadata["title"],
                text_content_file_path=document_metadata["text_content_file_path"]
            )
            db.session.add(document)
            db.session.commit()
        except Exception as e:
            if save_path and os.path.exists(save_path):
                os.remove(save_path)
            app.logger.error(f"⚠️ Database error: {str(e)}")
            return jsonify({"error": "Failed to save document info"}), 500

        # 5. Create payment intent and return response
        try:
            payment_data = _process_payment(analysis_cost)
            # Use current date if metadata date fails (fallback logic)
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return jsonify({
                "document_id": document.id,
                "title": document_metadata["title"],
                "original_filename": file.filename,
                "char_count": char_count,
                "file_size": os.path.getsize(save_path),
                "mime_type": file.content_type,
                "upload_date": upload_date,
                "analysis_cost": analysis_cost,
                "text_content_file_path": document_metadata["text_content_file_path"],
                **payment_data
            }), 200

        except Exception as e:
            if save_path and os.path.exists(save_path):
                os.remove(save_path)
            app.logger.error(f"⚠️ Payment error: {str(e)}")
            return jsonify({"error": "Payment setup failed"}), 500

    except Exception as e:
        if save_path and os.path.exists(save_path):
            os.remove(save_path)
        app.logger.error(f"❌ Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/payment/success", methods=["POST"])
def payment_success() -> Tuple[Response, int]:
    """
    Handle successful payment and trigger document analysis.

    Returns:
        Tuple[Response, int]: JSON response and HTTP status code
    """
    try:
        data = request.get_json()
        payment_intent_id = data.get("payment_intent_id")
        document_id = data.get("document_id")
        analysis_options = data.get("analysis_options", {})

        if not payment_intent_id or not document_id:
            return jsonify({"error": "Missing required parameters"}), 400

        # Verify payment intent
        payment_intent = confirm_payment_intent(payment_intent_id)
        if payment_intent.status != "succeeded":
            return jsonify({"error": "Payment not successful"}), 400

        # Get document and create payment record
        document = Document.query.get(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        payment = Payment(
            stripe_payment_id=payment_intent_id,
            amount=payment_intent.amount,
            currency=payment_intent.currency,
            status=payment_intent.status,
            document_id=document_id,
        )
        db.session.add(payment)

        # Read document content from the unique file
        text_content_file_path = document.text_content_file_path
        with open(text_content_file_path, "r", encoding="utf-8") as file:
            text_content = file.read()

        # Process document with AI by passing the document text content
        analysis_result = analyze_document(text_content, analysis_options)
        document.analysis_summary = analysis_result["summary"]
        db.session.commit()

        app.logger.info(f"✅ Document analysis completed for {document.id}")
        return jsonify({"success": True, "analysis": analysis_result}), 200

    except Exception as e:
        app.logger.error(f"❌ Payment processing error: {str(e)}")
        return jsonify({"error": str(e)}), 500
