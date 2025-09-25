import json
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from pydantic import BaseModel, Field

from config import settings
from models import SearchResponse, MissingInfo, MissingInfoType, EnrichmentSuggestion, ConfidenceLevel
from document_processor import DocumentProcessor

class StructuredOutputParser(BaseOutputParser):
    """Parse structured JSON output from LLM"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        try:
            # Extract JSON from the text (in case there's extra text)
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except json.JSONDecodeError as e:
            # Fallback parsing
            return {
                "answer": text,
                "confidence": 0.5,
                "missing_info": [],
                "enrichment_suggestions": []
            }

class RAGPipeline:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.output_parser = StructuredOutputParser()
        
        # Define prompts
        self.rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are an AI assistant that answers questions based on the provided context documents. 
            Analyze the context and provide a comprehensive answer to the user's question.

            Context Documents:
            {context}

            Question: {question}

            Please provide your response in the following JSON format:
            {{
                "answer": "Your detailed answer based on the context",
                "confidence": 0.85,
                "missing_info": [
                    {{
                        "type": "document|data|context|specific_fact",
                        "description": "What specific information is missing",
                        "suggested_action": "What action should be taken to get this information",
                        "priority": 1-5
                    }}
                ],
                "enrichment_suggestions": [
                    {{
                        "type": "document_type",
                        "description": "What kind of document would help",
                        "action": "Specific action to take",
                        "confidence": 0.8,
                        "estimated_effort": "low|medium|high"
                    }}
                ]
            }}

            Guidelines:
            1. If the context contains sufficient information, provide a confident answer (confidence > 0.7)
            2. If information is partially available, provide what you can and flag missing parts (confidence 0.4-0.7)
            3. If very little relevant information is available, be honest about limitations (confidence < 0.4)
            4. For missing_info, be specific about what's missing and why it's important
            5. For enrichment_suggestions, provide actionable recommendations
            6. Always base your answer primarily on the provided context
            """
        )
        
        self.completeness_prompt = PromptTemplate(
            input_variables=["answer", "question", "context"],
            template="""Analyze the completeness of this answer in relation to the question and available context.

            Question: {question}
            Answer: {answer}
            Available Context: {context}

            Rate the completeness and identify specific gaps. Respond in JSON format:
            {{
                "completeness_score": 0.85,
                "missing_aspects": [
                    "Specific aspect that's missing",
                    "Another missing aspect"
                ],
                "confidence_issues": [
                    "Areas where the answer is uncertain"
                ],
                "suggested_improvements": [
                    "How to improve the answer"
                ]
            }}
            """
        )

    def search_and_answer(self, query: str, include_confidence: bool = True, include_enrichment: bool = True) -> SearchResponse:
        """Main RAG pipeline: search, retrieve, and generate answer with completeness analysis"""
        start_time = time.time()
        
        try:
            # Step 1: Search for relevant documents
            search_results = self.document_processor.search_documents(query)
            
            if not search_results:
                return self._create_empty_response(query, start_time)
            
            # Step 2: Prepare context from search results
            context = self._prepare_context(search_results)
            
            # Step 3: Generate answer using LLM
            answer_data = self._generate_structured_answer(query, context)
            
            # Step 4: Analyze completeness if requested
            if include_confidence or include_enrichment:
                completeness_data = self._analyze_completeness(
                    answer_data.get("answer", ""), 
                    query, 
                    context
                )
                
                # Merge completeness analysis with answer data
                answer_data = self._merge_completeness_data(answer_data, completeness_data)
            
            # Step 5: Generate enrichment suggestions if requested
            if include_enrichment:
                enrichment_suggestions = self._generate_enrichment_suggestions(
                    answer_data.get("missing_info", []),
                    query,
                    search_results
                )
                answer_data["enrichment_suggestions"] = enrichment_suggestions
            
            # Step 6: Determine confidence level
            confidence = answer_data.get("confidence", 0.5)
            confidence_level = self._determine_confidence_level(confidence)
            
            # Step 7: Format response
            processing_time = time.time() - start_time
            
            return SearchResponse(
                answer=answer_data.get("answer", "I couldn't generate a proper answer."),
                confidence=confidence,
                confidence_level=confidence_level,
                sources=self._format_sources(search_results),
                missing_info=self._format_missing_info(answer_data.get("missing_info", [])),
                enrichment_suggestions=self._format_enrichment_suggestions(answer_data.get("enrichment_suggestions", [])),
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return SearchResponse(
                answer=f"Error processing your query: {str(e)}",
                confidence=0.0,
                confidence_level=ConfidenceLevel.LOW,
                sources=[],
                missing_info=[],
                enrichment_suggestions=[],
                processing_time=processing_time
            )

    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Prepare context string from search results"""
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"Document {i} (Source: {result['metadata']['filename']}, "
                f"Similarity: {result['similarity_score']:.2f}):\n"
                f"{result['content']}\n"
            )
        return "\n".join(context_parts)

    def _generate_structured_answer(self, query: str, context: str) -> Dict[str, Any]:
        """Generate structured answer using LLM"""
        try:
            prompt = self.rag_prompt.format(context=context, question=query)
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=2000
            )
            
            answer_text = response.choices[0].message.content
            return self.output_parser.parse(answer_text)
            
        except Exception as e:
            # Fallback to simple answer generation
            return {
                "answer": f"Based on the available documents, I found some relevant information, but encountered an error processing the structured response: {str(e)}",
                "confidence": 0.3,
                "missing_info": [],
                "enrichment_suggestions": []
            }

    def _analyze_completeness(self, answer: str, query: str, context: str) -> Dict[str, Any]:
        """Analyze the completeness of the answer"""
        try:
            prompt = self.completeness_prompt.format(
                answer=answer,
                question=query,
                context=context
            )
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            completeness_text = response.choices[0].message.content
            return self.output_parser.parse(completeness_text)
            
        except Exception as e:
            return {
                "completeness_score": 0.5,
                "missing_aspects": [],
                "confidence_issues": [f"Error analyzing completeness: {str(e)}"],
                "suggested_improvements": []
            }

    def _merge_completeness_data(self, answer_data: Dict[str, Any], completeness_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge completeness analysis with answer data"""
        # Adjust confidence based on completeness score
        completeness_score = completeness_data.get("completeness_score", 0.5)
        original_confidence = answer_data.get("confidence", 0.5)
        
        # Weighted average of original confidence and completeness
        adjusted_confidence = (original_confidence * 0.7) + (completeness_score * 0.3)
        answer_data["confidence"] = min(1.0, max(0.0, adjusted_confidence))
        
        # Add missing aspects to missing_info
        missing_aspects = completeness_data.get("missing_aspects", [])
        for aspect in missing_aspects:
            if "missing_info" not in answer_data:
                answer_data["missing_info"] = []
            
            answer_data["missing_info"].append({
                "type": "context",
                "description": aspect,
                "suggested_action": f"Find additional documents that cover: {aspect}",
                "priority": 3
            })
        
        return answer_data

    def _generate_enrichment_suggestions(self, missing_info: List[Dict], query: str, search_results: List[Dict]) -> List[Dict]:
        """Generate enrichment suggestions based on missing information and query"""
        suggestions = []
        
        # Analyze query type to suggest document types
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["how", "process", "steps", "procedure"]):
            suggestions.append({
                "type": "procedure_document",
                "description": "Step-by-step procedure or manual",
                "action": "Upload procedure documents, user manuals, or process guides",
                "confidence": 0.8,
                "estimated_effort": "medium"
            })
        
        if any(word in query_lower for word in ["what", "definition", "meaning", "is"]):
            suggestions.append({
                "type": "reference_document",
                "description": "Glossary, definitions, or reference material",
                "action": "Upload reference documents, glossaries, or specification sheets",
                "confidence": 0.7,
                "estimated_effort": "low"
            })
        
        if any(word in query_lower for word in ["when", "date", "time", "schedule"]):
            suggestions.append({
                "type": "temporal_document",
                "description": "Timeline, schedule, or date-specific information",
                "action": "Upload schedules, timelines, or historical records",
                "confidence": 0.8,
                "estimated_effort": "medium"
            })
        
        # Add suggestions based on missing info
        for info in missing_info:
            if info.get("type") == "specific_fact":
                suggestions.append({
                    "type": "factual_document",
                    "description": f"Document containing: {info.get('description', 'specific facts')}",
                    "action": info.get("suggested_action", "Find relevant documents"),
                    "confidence": 0.6,
                    "estimated_effort": "high"
                })
        
        # Remove duplicates and limit to top 5
        unique_suggestions = []
        seen_types = set()
        for suggestion in suggestions:
            if suggestion["type"] not in seen_types:
                unique_suggestions.append(suggestion)
                seen_types.add(suggestion["type"])
        
        return unique_suggestions[:5]

    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level based on confidence score"""
        if confidence >= settings.HIGH_CONFIDENCE_THRESHOLD:
            return ConfidenceLevel.HIGH
        elif confidence >= settings.MEDIUM_CONFIDENCE_THRESHOLD:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for response"""
        sources = []
        for result in search_results:
            sources.append({
                "filename": result["metadata"]["filename"],
                "similarity_score": result["similarity_score"],
                "chunk_index": result["metadata"]["chunk_index"],
                "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            })
        return sources

    def _format_missing_info(self, missing_info: List[Dict]) -> List[MissingInfo]:
        """Format missing info for response"""
        formatted = []
        for info in missing_info:
            formatted.append(MissingInfo(
                type=MissingInfoType(info.get("type", "context")),
                description=info.get("description", ""),
                suggested_action=info.get("suggested_action", ""),
                priority=info.get("priority", 3)
            ))
        return formatted

    def _format_enrichment_suggestions(self, suggestions: List[Dict]) -> List[EnrichmentSuggestion]:
        """Format enrichment suggestions for response"""
        formatted = []
        for suggestion in suggestions:
            formatted.append(EnrichmentSuggestion(
                type=suggestion.get("type", ""),
                description=suggestion.get("description", ""),
                action=suggestion.get("action", ""),
                confidence=suggestion.get("confidence", 0.5),
                estimated_effort=suggestion.get("estimated_effort", "medium")
            ))
        return formatted

    def _create_empty_response(self, query: str, start_time: float) -> SearchResponse:
        """Create response when no documents are found"""
        processing_time = time.time() - start_time
        
        return SearchResponse(
            answer="I couldn't find any relevant documents to answer your question. Please upload some documents first.",
            confidence=0.0,
            confidence_level=ConfidenceLevel.LOW,
            sources=[],
            missing_info=[MissingInfo(
                type=MissingInfoType.DOCUMENT,
                description="No relevant documents found in the knowledge base",
                suggested_action="Upload documents related to your question",
                priority=5
            )],
            enrichment_suggestions=[EnrichmentSuggestion(
                type="document_upload",
                description="Upload relevant documents to the knowledge base",
                action="Use the document upload feature to add files related to your question",
                confidence=1.0,
                estimated_effort="low"
            )],
            processing_time=processing_time
        )
