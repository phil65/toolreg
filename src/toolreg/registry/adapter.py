from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import TYPE_CHECKING

from lsprotocol import types


if TYPE_CHECKING:
    from collections.abc import Iterator

    from pygls.workspace import Workspace


@dataclass
class CodeBlock:
    """Python code block extracted from markdown."""

    content: str
    start_line: int
    end_line: int


class MarkdownAdapter:
    """Presents markdown files as notebooks to Ruff's LSP."""

    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self._markdown_files: dict[str, Path] = {}

    def extract_python_blocks(self, content: str) -> Iterator[CodeBlock]:
        """Extract Python code blocks from markdown content."""
        lines = content.splitlines(keepends=True)
        current_block: list[str] = []
        start_line = 0
        in_block = False

        for i, line in enumerate(lines):
            if line.startswith("```python"):
                in_block = True
                start_line = i + 1
                current_block = []
            elif line.startswith("```") and in_block:
                in_block = False
                yield CodeBlock(content="".join(current_block), start_line=start_line, end_line=i)
            elif in_block:
                current_block.append(line)

    def register_markdown_file(self, uri: str, content: str) -> None:
        """Register a markdown file as a notebook."""
        # Create notebook cells from Python blocks
        blocks = list(self.extract_python_blocks(content))

        # Create notebook document
        notebook = types.NotebookDocument(
            uri=uri,
            version=1,
            notebook_type="markdown-python",
            metadata={},
            cells=[
                types.NotebookCell(
                    kind=types.NotebookCellKind.Code,
                    document=f"{uri}#block{i}",
                    metadata={
                        "start_line": block.start_line,
                        "end_line": block.end_line,
                    },
                    execution_summary=None,
                )
                for i, block in enumerate(blocks)
            ],
        )

        # Create cell documents
        cell_documents = [
            types.TextDocumentItem(
                uri=cell.document, language_id="python", version=1, text=block.content
            )
            for cell, block in zip(notebook.cells, blocks)
        ]

        # Register with workspace
        params = types.DidOpenNotebookDocumentParams(
            notebook_document=notebook, cell_text_documents=cell_documents
        )
        self.workspace.put_notebook_document(params)
        self._markdown_files[uri] = Path(uri)

    def update_markdown_file(self, uri: str, content: str) -> None:
        """Update a markdown file's content."""
        # First remove old notebook
        if old_notebook := self.workspace.get_notebook_document(notebook_uri=uri):
            params = types.DidCloseNotebookDocumentParams(
                notebook_document=types.VersionedNotebookDocumentIdentifier(
                    uri=uri, version=old_notebook.version
                ),
                cell_text_documents=[
                    types.TextDocumentIdentifier(uri=cell.document) for cell in old_notebook.cells
                ],
            )
            self.workspace.remove_notebook_document(params)

        # Then register new content
        self.register_markdown_file(uri, content)

    def unregister_markdown_file(self, uri: str) -> None:
        """Unregister a markdown file."""
        if notebook := self.workspace.get_notebook_document(notebook_uri=uri):
            params = types.DidCloseNotebookDocumentParams(
                notebook_document=types.VersionedNotebookDocumentIdentifier(
                    uri=uri, version=notebook.version
                ),
                cell_text_documents=[
                    types.TextDocumentIdentifier(uri=cell.document) for cell in notebook.cells
                ],
            )
            self.workspace.remove_notebook_document(params)
            self._markdown_files.pop(uri, None)

    def map_diagnostic_to_markdown(
        self, uri: str, diagnostic: types.Diagnostic
    ) -> types.Diagnostic:
        """Map a diagnostic from cell position to markdown position."""
        notebook = self.workspace.get_notebook_document(notebook_uri=uri)
        if not notebook:
            return diagnostic

        # Find which cell this diagnostic belongs to
        cell_uri = re.match(f"{uri}#block(\\d+)", diagnostic.source or "")
        if not cell_uri:
            return diagnostic

        cell_idx = int(cell_uri.group(1))
        cell = notebook.cells[cell_idx]

        # Adjust position by cell's start line
        start_line = cell.metadata["start_line"]
        return types.Diagnostic(
            range=types.Range(
                start=types.Position(
                    line=diagnostic.range.start.line + start_line,
                    character=diagnostic.range.start.character,
                ),
                end=types.Position(
                    line=diagnostic.range.end.line + start_line,
                    character=diagnostic.range.end.character,
                ),
            ),
            message=diagnostic.message,
            severity=diagnostic.severity,
            code=diagnostic.code,
            source=diagnostic.source,
            tags=diagnostic.tags,
        )


"""
from ruff_lsp.__main__ import LSP_SERVER

# Create our adapter
markdown_adapter = MarkdownAdapter(LSP_SERVER.workspace)

# Hook into Ruff's LSP server
@LSP_SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(params: DidOpenTextDocumentParams) -> None:
    document = LSP_SERVER.workspace.get_text_document(params.text_document.uri)

    # Handle markdown files
    if document.language_id == "markdown":
        markdown_adapter.register_markdown_file(
            document.uri,
            document.source
        )
        return

    # Continue with normal processing
    # ... rest of Ruff's handler

@LSP_SERVER.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(params: DidCloseTextDocumentParams) -> None:
    document = LSP_SERVER.workspace.get_text_document(params.text_document.uri)

    if document.language_id == "markdown":
        markdown_adapter.unregister_markdown_file(document.uri)
        return
"""
