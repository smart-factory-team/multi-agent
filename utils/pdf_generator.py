"""PDF 보고서 생성 유틸리티"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from io import BytesIO
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import logging

logger = logging.getLogger(__name__)


class ChatbotReportGenerator:
    """챗봇 대화 내역 PDF 보고서 생성기"""
    
    def __init__(self):
        self.setup_fonts()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_fonts(self):
        """한글 폰트 설정 (다중 환경 지원)"""
        try:
            # 환경 강제 설정
            import os
            os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
            
            # 로케일 설정 시도
            try:
                import locale
                if os.name == 'nt':  # Windows
                    try:
                        locale.setlocale(locale.LC_ALL, 'Korean_Korea.utf8')
                    except:
                        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
                else:  # Linux/Mac
                    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
            except Exception as e:
                logger.warning(f"로케일 설정 실패: {e}")
            # 시스템 폰트 경로 시도 (UTF-8 지원 폰트들)
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
                "C:/Windows/Fonts/malgunbd.ttf",  # 맑은 고딕 Bold
                "C:/Windows/Fonts/gulim.ttc",  # 굴림
                "C:/Windows/Fonts/batang.ttc",  # 바탕
                "C:/Windows/Fonts/NanumGothic.ttf",  # 나눔고딕
                "C:/Windows/Fonts/NanumBarunGothic.ttf",  # 나눔바른고딕
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"  # Linux 대체
            ]
            
            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # 기존 폰트가 등록되어 있는지 확인
                        try:
                            pdfmetrics.getFont('Korean')
                            font_registered = True
                            logger.info(f"한글 폰트 이미 등록됨: Korean")
                            break
                        except:
                            # 폰트가 등록되지 않은 경우에만 등록
                            pdfmetrics.registerFont(TTFont('Korean', font_path))
                            font_registered = True
                            logger.info(f"한글 폰트 등록 성공: {font_path}")
                            break
                    except Exception as e:
                        logger.warning(f"폰트 등록 실패 {font_path}: {e}")
                        continue
            
            if not font_registered:
                logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
                self.font_name = 'Helvetica'
            else:
                self.font_name = 'Korean'
        
        except Exception as e:
            logger.error(f"폰트 설정 오류: {e}")
            self.font_name = 'Helvetica'
    
    def setup_custom_styles(self):
        """커스텀 스타일 설정"""
        self.custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Title'],
                fontName=self.font_name,
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2E86AB')
            ),
            'Heading': ParagraphStyle(
                'CustomHeading',
                parent=self.styles['Heading1'],
                fontName=self.font_name,
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12,
                textColor=colors.HexColor('#A23B72')
            ),
            'Normal': ParagraphStyle(
                'CustomNormal',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=6,
                alignment=TA_LEFT
            ),
            'UserMessage': ParagraphStyle(
                'CustomUserMessage',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=6,
                leftIndent=20,
                rightIndent=50,
                backColor=colors.HexColor('#E8F4FD')
            ),
            'BotMessage': ParagraphStyle(
                'CustomBotMessage',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=6,
                leftIndent=50,
                rightIndent=20,
                backColor=colors.HexColor('#F0F8E8')
            ),
            'Summary': ParagraphStyle(
                'CustomSummary',
                parent=self.styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=8,
                leftIndent=10,
                rightIndent=10,
                backColor=colors.HexColor('#FFF9E6'),
                borderColor=colors.HexColor('#F4A261'),
                borderWidth=1
            )
        }
    
    async def generate_chat_report(
        self,
        session_id: str,
        conversation_history: List[Dict[str, Any]],
        session_info: Dict[str, Any],
        final_summary: Optional[str] = None
    ) -> BytesIO:
        """대화 내역을 PDF 보고서로 생성"""
        try:
            # 입력 데이터 검증
            if not session_id:
                raise ValueError("session_id는 필수입니다")
            if not isinstance(conversation_history, list):
                conversation_history = []
            if not isinstance(session_info, dict):
                session_info = {}
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # 보고서 내용 구성
            story = []
            
            # 제목
            title = Paragraph("스마트팩토리 챗봇 상담 보고서", self.custom_styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 세션 정보
            story.extend(self._create_session_info_section(session_info))
            story.append(Spacer(1, 20))
            
            # 대화 내역
            story.extend(self._create_conversation_section(conversation_history))
            story.append(Spacer(1, 20))
            
            # 최종 요약 (있는 경우)
            if final_summary:
                story.extend(self._create_summary_section(final_summary))
            
            # 푸터
            story.extend(self._create_footer_section())
            
            # PDF 생성
            doc.build(story)
            buffer.seek(0)
            
            logger.info(f"PDF 보고서 생성 완료: {session_id}")
            return buffer
            
        except Exception as e:
            logger.error(f"PDF 보고서 생성 오류: {e}")
            logger.error(f"Session ID: {session_id}")
            logger.error(f"Conversation count: {len(conversation_history) if conversation_history else 0}")
            logger.error(f"Session info keys: {list(session_info.keys()) if session_info else []}")
            
            # 기본 PDF 생성 시도
            try:
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                story = [
                    Paragraph("PDF 생성 오류", self.custom_styles.get('Title', self.styles['Title'])),
                    Paragraph(f"오류: {str(e)}", self.custom_styles.get('Normal', self.styles['Normal'])),
                    Paragraph(f"세션 ID: {session_id}", self.custom_styles.get('Normal', self.styles['Normal']))
                ]
                doc.build(story)
                buffer.seek(0)
                logger.info(f"기본 오류 PDF 생성 완료: {session_id}")
                return buffer
            except Exception as fallback_error:
                logger.error(f"기본 PDF 생성도 실패: {fallback_error}")
                raise e
    
    def _create_session_info_section(self, session_info: Dict[str, Any]) -> List:
        """세션 정보 섹션 생성"""
        story = []
        
        # 세션 정보 제목
        heading = Paragraph("상담 정보", self.custom_styles['Heading'])
        story.append(heading)
        
        # 테이블 데이터 준비 - UTF-8 인코딩 보장
        data = [
            ['세션 ID', self._ensure_utf8_encoding(session_info.get('session_id', 'N/A'))],
            ['사용자 ID', self._ensure_utf8_encoding(session_info.get('user_id', 'N/A'))],
            ['이슈 코드', self._ensure_utf8_encoding(session_info.get('issue_code', 'N/A'))],
            ['상담 시작', self._ensure_utf8_encoding(session_info.get('created_at', 'N/A'))],
            ['상담 종료', self._ensure_utf8_encoding(session_info.get('ended_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))],
            ['총 대화 수', str(session_info.get('conversation_count', 0))],
            ['참여 에이전트', self._ensure_utf8_encoding(', '.join(session_info.get('participating_agents', [])))]
        ]
        
        # 테이블 생성
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6'))
        ]))
        
        story.append(table)
        return story
    
    def _create_conversation_section(self, conversation_history: List[Dict[str, Any]]) -> List:
        """대화 내역 섹션 생성"""
        story = []
        
        # 대화 내역 제목
        heading = Paragraph("대화 내역", self.custom_styles['Heading'])
        story.append(heading)
        
        if not conversation_history:
            no_conversation = Paragraph("대화 내역이 없습니다.", self.custom_styles['Normal'])
            story.append(no_conversation)
            return story
        
        # 각 대화 항목 처리
        for i, conversation in enumerate(conversation_history, 1):
            # 대화 번호
            conv_number = Paragraph(f"대화 {i}", 
                                   ParagraphStyle('ConvNumber', 
                                                parent=self.custom_styles['Normal'],
                                                fontName=self.font_name,
                                                fontSize=12,
                                                textColor=colors.HexColor('#495057'),
                                                spaceAfter=8))
            story.append(conv_number)
            
            # 사용자 메시지
            if conversation.get('user_message'):
                user_label = Paragraph("👤 사용자:", 
                                     ParagraphStyle('UserLabel',
                                                  parent=self.custom_styles['Normal'],
                                                  fontName=self.font_name,
                                                  fontSize=10,
                                                  textColor=colors.HexColor('#0056B3')))
                story.append(user_label)
                
                # UTF-8 인코딩 보장
                user_message = self._ensure_utf8_encoding(conversation['user_message'])
                user_msg = Paragraph(user_message, self.custom_styles['UserMessage'])
                story.append(user_msg)
                story.append(Spacer(1, 6))
            
            # 봇 응답
            if conversation.get('bot_response'):
                bot_label = Paragraph("🤖 챗봇:", 
                                    ParagraphStyle('BotLabel',
                                                 parent=self.custom_styles['Normal'],
                                                 fontName=self.font_name,
                                                 fontSize=10,
                                                 textColor=colors.HexColor('#28A745')))
                story.append(bot_label)
                
                # 봇 응답이 너무 길면 요약
                bot_response = conversation['bot_response']
                if len(bot_response) > 1000:
                    bot_response = bot_response[:1000] + "... (내용이 길어 요약됨)"
                
                # UTF-8 인코딩 보장
                bot_response = self._ensure_utf8_encoding(bot_response)
                bot_msg = Paragraph(bot_response, self.custom_styles['BotMessage'])
                story.append(bot_msg)
            
            # 타임스탬프
            if conversation.get('timestamp'):
                timestamp = Paragraph(f"시간: {conversation['timestamp']}", 
                                    ParagraphStyle('Timestamp',
                                                 parent=self.custom_styles['Normal'],
                                                 fontName=self.font_name,
                                                 fontSize=8,
                                                 textColor=colors.HexColor('#6C757D'),
                                                 alignment=TA_RIGHT))
                story.append(timestamp)
            
            story.append(Spacer(1, 15))
        
        return story
    
    def _ensure_utf8_encoding(self, text: str) -> str:
        """텍스트의 UTF-8 인코딩 보장 (강화된 버전)"""
        if not text:
            return ""
        
        try:
            # 이미 문자열인 경우
            if isinstance(text, str):
                # 1단계: 기본 UTF-8 안전성 확보
                try:
                    text = text.encode('utf-8', errors='replace').decode('utf-8')
                except:
                    # 인코딩 실패시 강제 변환
                    text = str(text).encode('utf-8', errors='replace').decode('utf-8')
                
                # 2단계: 문제가 될 수 있는 특수문자 처리
                text = text.replace('\u200b', '')  # 제로폭 공백 제거
                text = text.replace('\ufeff', '')  # BOM 제거  
                text = text.replace('\x00', '')    # NULL 문자 제거
                
                # 3단계: ReportLab에서 문제가 되는 문자들 처리
                problematic_chars = {
                    '\u2028': '\n',  # Line separator
                    '\u2029': '\n',  # Paragraph separator
                    '\u00a0': ' ',   # Non-breaking space
                }
                for old, new in problematic_chars.items():
                    text = text.replace(old, new)
                
                return text
            else:
                # bytes인 경우 UTF-8로 디코딩
                return text.decode('utf-8', errors='replace')
                
        except Exception as e:
            logger.warning(f"UTF-8 인코딩 처리 중 오류: {e} - 텍스트: {str(text)[:50]}...")
            # 최후의 수단: 안전한 변환
            try:
                safe_text = str(text).encode('ascii', errors='ignore').decode('ascii')
                return safe_text if safe_text else "[텍스트 변환 실패]"
            except:
                return "[텍스트 변환 실패]"
    
    def _create_summary_section(self, final_summary: str) -> List:
        """최종 요약 섹션 생성"""
        story = []
        
        # 요약 제목
        heading = Paragraph("상담 요약", self.custom_styles['Heading'])
        story.append(heading)
        
        # 요약 내용 - UTF-8 인코딩 보장
        final_summary = self._ensure_utf8_encoding(final_summary)
        summary = Paragraph(final_summary, self.custom_styles['Summary'])
        story.append(summary)
        
        return story
    
    def _create_footer_section(self) -> List:
        """푸터 섹션 생성"""
        story = []
        
        story.append(Spacer(1, 30))
        
        # 생성 정보
        footer_info = f"본 보고서는 {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}에 자동 생성되었습니다."
        footer = Paragraph(footer_info, 
                         ParagraphStyle('Footer',
                                      parent=self.custom_styles['Normal'],
                                      fontName=self.font_name,
                                      fontSize=9,
                                      textColor=colors.HexColor('#6C757D'),
                                      alignment=TA_CENTER))
        story.append(footer)
        
        # 회사 정보
        company_info = "스마트팩토리 AI 챗봇 시스템"
        company = Paragraph(company_info,
                          ParagraphStyle('Company',
                                       parent=self.custom_styles['Normal'],
                                       fontName=self.font_name,
                                       fontSize=8,
                                       textColor=colors.HexColor('#6C757D'),
                                       alignment=TA_CENTER))
        story.append(company)
        
        return story


# 전역 인스턴스
pdf_generator = ChatbotReportGenerator()


async def generate_session_report(
    session_id: str,
    conversation_history: List[Dict[str, Any]],
    session_info: Dict[str, Any],
    final_summary: Optional[str] = None
) -> BytesIO:
    """세션 보고서 생성 (편의 함수)"""
    return await pdf_generator.generate_chat_report(
        session_id, conversation_history, session_info, final_summary
    )