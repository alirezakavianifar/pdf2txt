"""
PyQt5 GUI Application for PDF Processing Pipeline
"""
import sys
import json
import io
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QCheckBox, QProgressBar,
    QFileDialog, QListWidget, QTabWidget, QMessageBox, QGroupBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QTextCharFormat, QColor

from run_complete_pipeline import run_pipeline


class StreamCapture(io.StringIO):
    """Custom stream handler that emits Qt signals for log messages."""
    
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        
    def write(self, text):
        if text.strip():  # Only emit non-empty lines
            self.signal.emit(text)
        return len(text)
    
    def flush(self):
        pass


class PipelineWorker(QThread):
    """Worker thread to run the pipeline without freezing the UI."""
    
    # Signals
    log_message = pyqtSignal(str)
    progress_update = pyqtSignal(int, int)  # current, total
    status_update = pyqtSignal(str)
    finished = pyqtSignal(dict)  # merged_data (single file) or None (batch mode)
    batch_finished = pyqtSignal(list)  # List of (filename, merged_data) tuples for batch mode
    error = pyqtSignal(str)
    
    def __init__(self, pdf_paths: list[str], export_excel: bool = False, export_access: bool = False):
        super().__init__()
        self.pdf_paths = pdf_paths  # List of file paths
        self.export_excel = export_excel
        self.export_access = export_access
        self._is_cancelled = False
        
    def cancel(self):
        """Cancel the processing."""
        self._is_cancelled = True
        
    def run(self):
        """Run the pipeline in the background thread."""
        try:
            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stream_capture = StreamCapture(self.log_message)
            sys.stdout = stream_capture
            sys.stderr = stream_capture
            
            try:
                # Process list of files
                total_files = len(self.pdf_paths)
                
                if total_files == 0:
                    self.error.emit("No PDF files selected.")
                    return
                
                # If single file, use finished signal; otherwise use batch_finished
                if total_files == 1:
                    # Single file mode
                    pdf_path = self.pdf_paths[0]
                    self.status_update.emit(f"Processing {Path(pdf_path).name}...")
                    self.progress_update.emit(0, 1)  # Indeterminate mode
                    
                    merged_data = run_pipeline(pdf_path, export_excel=self.export_excel)
                    
                    if merged_data:
                        self.progress_update.emit(1, 1)
                        self.finished.emit(merged_data)
                    else:
                        self.error.emit("Pipeline returned no data")
                else:
                    # Batch mode - process multiple files
                    self.status_update.emit(f"Processing {total_files} PDF files...")
                    bills_data = []
                    errors = 0
                    
                    for i, pdf_path in enumerate(self.pdf_paths, start=1):
                        if self._is_cancelled:
                            self.status_update.emit("Processing cancelled")
                            return
                        
                        pdf_file = Path(pdf_path)
                        self.progress_update.emit(i, total_files)
                        self.status_update.emit(f"Processing {i}/{total_files}: {pdf_file.name}")
                        
                        try:
                            merged_data = run_pipeline(str(pdf_path), export_excel=False)
                            if merged_data:
                                bills_data.append((pdf_file.name, merged_data))
                        except Exception as e:
                            errors += 1
                            self.log_message.emit(f"[ERROR] Failed processing {pdf_file.name}: {e}\n")
                    
                    # Batch processing complete
                    self.progress_update.emit(total_files, total_files)
                    self.status_update.emit(f"Batch complete: {len(bills_data)} succeeded, {errors} failed")
                    
                    # Emit batch results
                    if bills_data:
                        self.batch_finished.emit(bills_data)
                    else:
                        self.error.emit("No files were processed successfully.")
                        
            finally:
                # Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.error.emit(error_details)


class PDFPipelineGUI(QMainWindow):
    """Main GUI window for PDF processing pipeline."""
    
    def __init__(self):
        super().__init__()
        self.worker: Optional[PipelineWorker] = None
        self.selected_files: list[Path] = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Processing Pipeline")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # === File Selection Section ===
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        # File selection (supports multiple PDF files)
        select_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.select_files)
        select_layout.addWidget(QLabel("Select PDF Files:"))
        select_layout.addWidget(self.browse_btn)
        select_layout.addStretch()
        file_layout.addLayout(select_layout)
        
        # File list (shows selected PDF files)
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(120)
        file_layout.addWidget(self.file_list)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # === Options Section ===
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()
        self.excel_checkbox = QCheckBox("Export to Excel")
        self.excel_checkbox.setChecked(False)
        self.access_checkbox = QCheckBox("Export to Access")
        self.access_checkbox.setChecked(False)
        options_layout.addWidget(self.excel_checkbox)
        options_layout.addWidget(self.access_checkbox)
        options_layout.addStretch()
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # === Controls Section ===
        controls_layout = QHBoxLayout()
        self.process_btn = QPushButton("Process")
        self.process_btn.setMinimumHeight(35)
        self.process_btn.clicked.connect(self.start_processing)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setMinimumHeight(35)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_processing)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate by default
        self.progress_bar.setVisible(False)
        
        controls_layout.addWidget(self.process_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.progress_bar, stretch=1)
        main_layout.addLayout(controls_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # === Output Tabs ===
        tabs = QTabWidget()
        
        # Logs tab
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        tabs.addTab(self.log_text, "Logs")
        
        # JSON Preview tab
        self.json_text = QTextEdit()
        self.json_text.setReadOnly(True)
        self.json_text.setFont(QFont("Consolas", 9))
        self.json_text.setPlaceholderText("JSON output will appear here after processing...")
        tabs.addTab(self.json_text, "JSON Preview")
        
        main_layout.addWidget(tabs, stretch=1)
        
        # Initial log message
        self.update_log("PDF Processing Pipeline GUI\n" + "=" * 50 + "\n")
        self.update_log("Ready to process PDF files.\n")
        self.update_log("Click 'Browse...' to select one or more PDF files, then click 'Process' to begin.\n\n")
        
    def select_files(self):
        """Open file dialog to select one or more PDF files."""
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF File(s)", 
            str(Path.cwd()), "PDF Files (*.pdf)"
        )
        
        if paths:
            # Filter to only PDF files
            self.selected_files = [Path(p) for p in paths if Path(p).suffix.lower() == '.pdf']
            
            if not self.selected_files:
                QMessageBox.warning(
                    self, "Invalid Selection",
                    "Please select at least one PDF file."
                )
                return
            
            # Update file list
            self.file_list.clear()
            for pdf_file in self.selected_files:
                self.file_list.addItem(pdf_file.name)
            
            count = len(self.selected_files)
            self.update_log(f"Selected {count} PDF file(s):\n")
            for pdf_file in self.selected_files:
                self.update_log(f"  - {pdf_file.name}\n")
            self.update_log("\n")
                
    def start_processing(self):
        """Start the pipeline processing."""
        if not self.selected_files:
            QMessageBox.warning(
                self, "No Selection",
                "Please select at least one PDF file first."
            )
            return
        
        # Validate all selected files exist
        missing_files = [f for f in self.selected_files if not f.exists()]
        if missing_files:
            QMessageBox.warning(
                self, "Invalid Files",
                f"The following files do not exist:\n" + "\n".join([str(f) for f in missing_files])
            )
            return
            
        # Disable controls
        self.process_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate
        
        # Clear previous results
        self.json_text.clear()
        self.update_log("\n" + "=" * 50 + "\n")
        self.update_log("Starting processing...\n\n")
        
        # Create and start worker thread
        export_excel = self.excel_checkbox.isChecked()
        export_access = self.access_checkbox.isChecked()
        # Pass list of file paths
        file_paths = [str(f) for f in self.selected_files]
        self.worker = PipelineWorker(file_paths, export_excel=export_excel, export_access=export_access)
        
        # Connect signals
        self.worker.log_message.connect(self.update_log)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.handle_pipeline_finished)
        self.worker.batch_finished.connect(self.handle_batch_finished)
        self.worker.error.connect(self.handle_error)
        
        # Start processing
        self.worker.start()
        
    def stop_processing(self):
        """Stop the pipeline processing."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.requestInterruption()
            # Give it a moment to stop gracefully
            if not self.worker.wait(1000):  # Wait up to 1 second
                # Force terminate if it doesn't stop
                self.worker.terminate()
                self.worker.wait()
            self.update_log("\n[STOPPED] Processing cancelled by user.\n\n")
            self.update_status("Cancelled")
            self.reset_controls()
            self.worker = None
            
    def update_log(self, message: str):
        """Append message to log display."""
        self.log_text.moveCursor(self.log_text.textCursor().End)
        self.log_text.insertPlainText(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def update_progress(self, current: int, total: int):
        """Update progress bar."""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
        else:
            self.progress_bar.setMaximum(0)  # Indeterminate
            
    def update_status(self, message: str):
        """Update status label."""
        self.status_label.setText(message)
        
    def handle_pipeline_finished(self, merged_data: dict):
        """Handle single file pipeline completion."""
        self.update_log("\n" + "=" * 50 + "\n")
        self.update_log("Processing completed successfully!\n\n")
        
        # Update JSON preview
        self.update_json_preview(merged_data)
        
        # Prepare bills data for export
        if self.selected_files:
            bills_data = [(self.selected_files[0].name, merged_data)]
        else:
            bills_data = [("unknown.pdf", merged_data)]
        
        # Handle Excel export if needed
        if self.excel_checkbox.isChecked():
            try:
                from run_complete_pipeline import export_to_excel
                output_root = Path("output")
                excel_path = output_root / "bills_export.xlsx"
                export_to_excel(bills_data, excel_path)
                self.update_log(f"Excel file exported to: {excel_path}\n")
                QMessageBox.information(
                    self, "Export Complete",
                    f"Excel file saved to:\n{excel_path}"
                )
            except Exception as e:
                self.update_log(f"Error exporting to Excel: {e}\n")
                QMessageBox.warning(self, "Export Error", f"Failed to export to Excel:\n{str(e)}")
        
        # Handle Access export if needed
        if self.access_checkbox.isChecked():
            try:
                from run_complete_pipeline import export_to_access
                output_root = Path("output")
                access_path = output_root / "bills_export.accdb"
                export_to_access(bills_data, access_path)
                self.update_log(f"Access database exported to: {access_path}\n")
                QMessageBox.information(
                    self, "Export Complete",
                    f"Access database saved to:\n{access_path}"
                )
            except ImportError as e:
                self.update_log(f"Error exporting to Access: {e}\n")
                QMessageBox.warning(
                    self, "Export Error",
                    f"Failed to export to Access:\n{str(e)}\n\n"
                    "Please install pyodbc: pip install pyodbc"
                )
            except Exception as e:
                self.update_log(f"Error exporting to Access: {e}\n")
                QMessageBox.warning(self, "Export Error", f"Failed to export to Access:\n{str(e)}")
        
        self.update_status("Completed")
        self.reset_controls()
        self.worker = None
        
    def handle_batch_finished(self, bills_data: list):
        """Handle batch processing completion."""
        self.update_log("\n" + "=" * 50 + "\n")
        self.update_log(f"Batch processing completed! Processed {len(bills_data)} file(s).\n\n")
        
        # Show summary of first file's data in JSON preview
        if bills_data:
            first_filename, first_data = bills_data[0]
            self.update_json_preview({
                "batch_summary": {
                    "total_files": len(bills_data),
                    "files": [filename for filename, _ in bills_data]
                },
                "sample_data": {
                    "file": first_filename,
                    "data": first_data
                }
            })
        
        # Handle Excel export if needed
        if self.excel_checkbox.isChecked():
            try:
                from run_complete_pipeline import export_to_excel
                output_root = Path("output")
                excel_path = output_root / "bills_export.xlsx"
                
                export_to_excel(bills_data, excel_path)
                self.update_log(f"Excel file exported to: {excel_path}\n")
                self.update_log(f"  - Total rows: {len(bills_data)}\n")
                QMessageBox.information(
                    self, "Export Complete",
                    f"Excel file saved to:\n{excel_path}\n\n"
                    f"Total rows: {len(bills_data)}"
                )
            except Exception as e:
                self.update_log(f"Error exporting to Excel: {e}\n")
                QMessageBox.warning(self, "Export Error", f"Failed to export to Excel:\n{str(e)}")
        
        # Handle Access export if needed
        if self.access_checkbox.isChecked():
            try:
                from run_complete_pipeline import export_to_access
                output_root = Path("output")
                access_path = output_root / "bills_export.accdb"
                export_to_access(bills_data, access_path)
                self.update_log(f"Access database exported to: {access_path}\n")
                self.update_log(f"  - Total rows: {len(bills_data)}\n")
                QMessageBox.information(
                    self, "Export Complete",
                    f"Access database saved to:\n{access_path}\n\n"
                    f"Total rows: {len(bills_data)}"
                )
            except ImportError as e:
                self.update_log(f"Error exporting to Access: {e}\n")
                QMessageBox.warning(
                    self, "Export Error",
                    f"Failed to export to Access:\n{str(e)}\n\n"
                    "Please install pyodbc: pip install pyodbc"
                )
            except Exception as e:
                self.update_log(f"Error exporting to Access: {e}\n")
                QMessageBox.warning(self, "Export Error", f"Failed to export to Access:\n{str(e)}")
        
        self.update_status(f"Batch completed: {len(bills_data)} file(s)")
        self.reset_controls()
        self.worker = None
        
    def handle_error(self, error_message: str):
        """Handle pipeline errors."""
        self.update_log("\n" + "=" * 50 + "\n")
        
        # Format error in red
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        error_format = QTextCharFormat()
        error_format.setForeground(QColor("#ff6b6b"))
        error_format.setFontWeight(700)  # Bold
        cursor.setCharFormat(error_format)
        cursor.insertText(f"[ERROR] {error_message}\n\n")
        
        # Reset format
        normal_format = QTextCharFormat()
        normal_format.setForeground(QColor("#d4d4d4"))
        cursor.setCharFormat(normal_format)
        
        self.update_status("Error occurred")
        
        # Show error dialog with details
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Processing Error")
        error_dialog.setText("An error occurred during processing:")
        error_dialog.setDetailedText(error_message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()
        
        self.reset_controls()
        
    def update_json_preview(self, data: dict):
        """Update JSON preview with formatted data."""
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            self.json_text.setPlainText(json_str)
        except Exception as e:
            self.json_text.setPlainText(f"Error formatting JSON: {str(e)}")
            
    def reset_controls(self):
        """Reset UI controls after processing."""
        self.process_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.browse_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        # Clean up worker reference
        if self.worker:
            if self.worker.isRunning():
                self.worker.wait()
            self.worker = None


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern look
    
    window = PDFPipelineGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

