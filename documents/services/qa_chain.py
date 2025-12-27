from typing import List, Optional, Tuple

from django.conf import settings
from django.utils import timezone


class QAChainService:
    """
    Question-Answering chain service using LangChain.

    Generates answers to questions based on retrieved document content.
    Supports both HuggingFace models and FakeLLM for testing.
    """

    def __init__(self):
        self._llm = None
        self._chain = None
        self._initialized = False

    def _initialize(self):
        """Initialize the LLM and chain lazily."""
        if self._initialized:
            return

        use_fake = getattr(settings, 'USE_FAKE_LLM', True)

        if use_fake:
            self._init_fake_llm()
        else:
            self._init_huggingface_llm()

        self._initialized = True

    def _init_fake_llm(self):
        """Initialize FakeLLM for testing."""
        from langchain_community.llms.fake import FakeListLLM

        responses = [
            "Based on the provided documents, I can provide the following answer. "
            "The information suggests that the topic relates to the content in the retrieved documents. "
            "Please note this is a simulated response for testing purposes."
        ]
        self._llm = FakeListLLM(responses=responses)

    def _init_huggingface_llm(self):
        """Initialize HuggingFace LLM."""
        from langchain_huggingface import HuggingFacePipeline
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

        model_name = getattr(settings, 'HUGGINGFACE_MODEL', 'google/flan-t5-base')

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            temperature=0.7,
        )

        self._llm = HuggingFacePipeline(pipeline=pipe)

    def _build_prompt(self, question: str, context: str) -> str:
        """Build the prompt for the LLM."""
        return f"""Answer the question based only on the following context.
If the answer cannot be found in the context, say "I cannot find the answer in the provided documents."

Context:
{context}

Question: {question}

Answer:"""

    def generate_answer(
        self,
        question: str,
        documents: List[Tuple[any, float]],
    ) -> str:
        """
        Generate an answer based on retrieved documents.

        Args:
            question: The user's question.
            documents: List of (Document, score) tuples from retrieval.

        Returns:
            str: The generated answer.
        """
        self._initialize()

        if not documents:
            return "No relevant documents found to answer this question."

        context_parts = []
        for doc, score in documents:
            context_parts.append(
                f"[Document: {doc.title}]\n{doc.content}\n"
            )

        context = "\n---\n".join(context_parts)

        if len(context) > 4000:
            context = context[:4000] + "...[truncated]"

        prompt = self._build_prompt(question, context)

        try:
            response = self._llm.invoke(prompt)
            if hasattr(response, 'content'):
                return response.content
            return str(response)
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def answer_question(self, question_obj) -> str:
        """
        Generate and save answer for a Question model instance.

        Args:
            question_obj: Question model instance.

        Returns:
            str: The generated answer.
        """
        from .retriever import get_retriever

        retriever = get_retriever()

        if not retriever.is_indexed:
            from .retriever import refresh_index
            refresh_index()

        documents = retriever.find_relevant_documents(
            question_obj.text,
            top_k=3,
            min_score=0.05
        )

        answer = self.generate_answer(question_obj.text, documents)

        question_obj.answer = answer
        question_obj.answered_at = timezone.now()

        question_obj.related_documents.clear()
        for doc, score in documents:
            question_obj.related_documents.add(doc)

        question_obj.save()

        return answer


_qa_service_instance: Optional[QAChainService] = None


def get_qa_service() -> QAChainService:
    """
    Get the singleton QAChainService instance.

    Returns:
        QAChainService: The shared QA service instance.
    """
    global _qa_service_instance
    if _qa_service_instance is None:
        _qa_service_instance = QAChainService()
    return _qa_service_instance
