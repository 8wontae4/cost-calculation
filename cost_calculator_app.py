import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def format_number_input(label, value, min_value=0, max_value=None, step=1, help_text=None, format_str="%d"):
    """숫자 입력 필드에 천 단위 구분자를 표시하는 사용자 정의 함수"""
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        input_value = st.number_input(
            label,
            min_value=min_value,
            max_value=max_value,
            value=value,
            step=step,
            format=format_str,
            help=help_text,
            key=f"input_{label}"
        )
    with col2:
        if input_value >= 1000:
            st.caption(f"{input_value:,}")
    return input_value

def main():
    st.set_page_config(
        page_title="광모듈 생산 비용 계산기",
        page_icon="🔬",
        layout="wide"
    )

    st.title("🔬 광모듈 생산 비용 계산기")
    st.markdown("---")

    # 사이드바 입력
    st.sidebar.header("📊 입력 파라미터")

    # 생산 계획 섹션
    st.sidebar.subheader("🏭 생산 계획")
    production_period_months = st.sidebar.number_input(
        "생산 기간 (개월)",
        min_value=1,
        max_value=60,
        value=12,
        help="GLAB 장비를 생산할 기간을 개월 단위로 입력하세요"
    )

    target_glab_sales = format_number_input(
        "목표 GLAB 판매량 (대)",
        value=600,
        min_value=1,
        help_text="생산 기간 동안 판매할 GLAB 장비 수량"
    )

    # 월간 GLAB 생산 가능량 자동 계산
    monthly_glab_capacity = target_glab_sales / production_period_months
    st.sidebar.write(f"**월간 GLAB 생산 가능량**: {monthly_glab_capacity:.1f}대/월")
    st.sidebar.caption("목표 판매량 ÷ 생산 기간으로 자동 계산됩니다. GLab 1대당 광모듈 12개 필요함.")

    # 납품 가격 섹션
    st.sidebar.subheader("💰 광모듈 납품 가격")
    optical_module_set_price = st.sidebar.number_input(
        "광모듈 12대 납품가격 (천만원)",
        min_value=0.1,
        value=5.0,
        step=0.1,
        format="%.1f",
        help="광모듈 12대 세트(GLAB 1대분)의 납품 가격 (천만원 단위)"
    )
    optical_module_price_won = optical_module_set_price * 10000000 / 12  # 12대 가격을 1대 가격으로 변환

    # 부품 단가 섹션
    st.sidebar.subheader("💰 부품 단가")
    optical_block_price = format_number_input(
        "광블럭 단가 (원/개)",
        value=140000,
        help_text="광블럭 1개의 단가"
    )

    optical_quartz_price = format_number_input(
        "광석영 단가 (원/개)",
        value=3750,
        help_text="광석영 1개의 단가 (광블럭 1개당 16개 필요)"
    )

    other_parts_price = format_number_input(
        "기타 부품 단가 (원/개)",
        value=1000,
        help_text="기타 부품의 단가"
    )

    # 인력 비용 섹션
    st.sidebar.subheader("👥 인력 비용")
    required_workers = st.sidebar.number_input(
        "조립 작업 필요 인력 (명)",
        min_value=1,
        value=1,
        help="광모듈 조립 작업에 필요한 인력 수"
    )

    annual_salary = format_number_input(
        "인력당 연봉 (원/년)",
        value=40000000,
        help_text="조립 작업 인력 1명의 연봉"
    )

    # 초기 투자 비용
    st.sidebar.subheader("🏗️ 초기 투자")
    initial_setup_cost = format_number_input(
        "초기 설비 투자 비용 (원)",
        value=30000000,
        help_text="장비, 작업대 등 초기 셋팅 비용"
    )

    depreciation_period_years = st.sidebar.number_input(
        "감가상각 기간 (년)",
        min_value=1,
        max_value=20,
        value=5,
        help="초기 설비 투자비용의 감가상각 기간"
    )

    # 계산 로직
    calculations = calculate_costs(
        production_period_months,
        target_glab_sales,
        monthly_glab_capacity,
        optical_block_price,
        optical_quartz_price,
        other_parts_price,
        required_workers,
        annual_salary,
        initial_setup_cost,
        depreciation_period_years,
        optical_module_price_won
    )

    # 메인 화면 결과 표시
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 생산 계획 분석")

        # 기본 정보 표시
        st.metric("연간 GLAB 생산 Capacity", f"{calculations['annual_glab_capacity']:,}대")
        st.metric("필요 광모듈 수량 (총)", f"{calculations['total_optical_modules']:,}개")
        st.metric("월간 광모듈 생산량", f"{calculations['monthly_optical_modules']:,}개/월")
        st.metric("일간 광모듈 생산량", f"{calculations['daily_optical_modules']:,}개/일")


    with col2:
        st.subheader("💵 비용 분석")

        # 주요 비용 지표
        st.metric("광블럭 제조원가", f"{calculations['optical_block_manufacturing_cost']:,}원/개")
        st.metric("총 재료비", f"{calculations['total_material_cost']:,}원")
        st.metric("총 인건비", f"{calculations['total_labor_cost']:,}원")
        st.metric("총 생산 비용", f"{calculations['total_production_cost']:,}원",
                 help="재료비 + 인건비 + 감가상각비")
        st.metric("연간 감가상각비", f"{calculations['annual_depreciation']:,}원")

    # 매출이익 예상
    st.subheader("💰 매출이익 예상")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("연간 예상 매출", f"{calculations['annual_revenue']:,}원")
        st.caption(f"{calculations['annual_revenue']/100000000:.1f}억원")
    with col2:
        st.metric("연간 총 생산비용", f"{calculations['annual_production_cost']:,}원")
        st.caption(f"{calculations['annual_production_cost']/100000000:.1f}억원")
    with col3:
        st.metric("연간 예상 이익", f"{calculations['annual_profit']:,}원",
                 delta=f"{calculations['profit_margin']:.1f}%")
        st.caption(f"{calculations['annual_profit']/100000000:.1f}억원")

    # 상세 비용 분석
    st.subheader("📊 상세 비용 분석")

    # 비용 구성 차트
    col1, col2 = st.columns(2)

    with col1:
        # 파이 차트 - 비용 구성
        cost_breakdown = {
            '재료비': calculations['total_material_cost'],
            '인건비': calculations['total_labor_cost'],
            '감가상각비': calculations['depreciation_cost']
        }

        fig_pie = px.pie(
            values=list(cost_breakdown.values()),
            names=list(cost_breakdown.keys()),
            title="총 비용 구성"
        )
        st.plotly_chart(fig_pie, config={'displayModeBar': False})

    with col2:
        # 바 차트 - 재료비 세부 구성
        material_breakdown = {
            '광블럭': optical_block_price * calculations['total_optical_modules'],
            '광석영 (16개/블럭)': optical_quartz_price * 16 * calculations['total_optical_modules'],
            '기타 부품': other_parts_price * calculations['total_optical_modules']
        }

        fig_bar = px.bar(
            x=list(material_breakdown.keys()),
            y=list(material_breakdown.values()),
            title="재료비 세부 구성"
        )
        fig_bar.update_layout(yaxis_title="비용 (원)")
        st.plotly_chart(fig_bar, config={'displayModeBar': False})

    # 상세 계산 결과 테이블
    st.subheader("📋 상세 계산 결과")

    results_data = {
        '항목': [
            '생산 기간',
            '목표 GLAB 판매량',
            '월간 GLAB 생산 가능량',
            '연간 GLAB 생산 Capacity',
            '필요 광모듈 수량 (총)',
            '월간 광모듈 생산량',
            '일간 광모듈 생산량',
            '광블럭 제조원가',
            '총 재료비',
            '총 인건비',
            '광모듈 12대 납품가격',
            '연간 감가상각비',
            '총 생산 비용',
            '연간 예상 매출',
            '연간 예상 이익'
        ],
        '값': [
            f"{production_period_months}개월",
            f"{target_glab_sales:,}대",
            f"{monthly_glab_capacity:.1f}대/월",
            f"{calculations['annual_glab_capacity']:.1f}대/년",
            f"{calculations['total_optical_modules']:,}개",
            f"{calculations['monthly_optical_modules']:,}개/월",
            f"{calculations['daily_optical_modules']:,}개/일",
            f"{calculations['optical_block_manufacturing_cost']:,}원/개",
            f"{calculations['total_material_cost']:,}원",
            f"{calculations['total_labor_cost']:,}원",
            f"{optical_module_set_price:.1f}천만원",
            f"{calculations['annual_depreciation']:,}원",
            f"{calculations['total_production_cost']:,}원",
            f"{calculations['annual_revenue']:,}원",
            f"{calculations['annual_profit']:,}원"
        ]
    }

    df_results = pd.DataFrame(results_data)
    st.dataframe(df_results, width='stretch', hide_index=True)

    # 다운로드 기능
    st.subheader("💾 결과 다운로드")
    csv = df_results.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSV로 다운로드",
        data=csv,
        file_name="광모듈_생산_비용_계산_결과.csv",
        mime="text/csv"
    )

def calculate_costs(production_period_months, target_glab_sales, monthly_glab_capacity,
                   optical_block_price, optical_quartz_price, other_parts_price,
                   required_workers, annual_salary, initial_setup_cost,
                   depreciation_period_years, optical_module_price_won):

    # 기본 계산
    annual_glab_capacity = monthly_glab_capacity * 12
    modules_per_glab = 12
    total_optical_modules = target_glab_sales * modules_per_glab

    # 월간/일간 생산량
    monthly_optical_modules = total_optical_modules / production_period_months
    daily_optical_modules = monthly_optical_modules / 30

    # 생산 가능성 분석
    required_glab_per_month = target_glab_sales / production_period_months
    production_feasible = required_glab_per_month <= monthly_glab_capacity
    capacity_shortage = max(0, target_glab_sales - (annual_glab_capacity * production_period_months / 12))

    # 비용 계산
    optical_quartz_cost_per_block = optical_quartz_price * 16
    optical_block_manufacturing_cost = optical_block_price + optical_quartz_cost_per_block + other_parts_price

    total_material_cost = optical_block_manufacturing_cost * total_optical_modules
    total_labor_cost = annual_salary * required_workers * (production_period_months / 12)

    # 감가상각 계산
    annual_depreciation = initial_setup_cost / depreciation_period_years
    depreciation_cost = annual_depreciation * (production_period_months / 12)

    total_production_cost = total_material_cost + total_labor_cost + depreciation_cost

    # 매출 및 이익 계산
    annual_optical_modules = total_optical_modules * (12 / production_period_months)
    annual_revenue = annual_optical_modules * optical_module_price_won
    annual_production_cost = (total_material_cost + total_labor_cost) * (12 / production_period_months) + annual_depreciation
    annual_profit = annual_revenue - annual_production_cost
    profit_margin = (annual_profit / annual_revenue) * 100 if annual_revenue > 0 else 0

    return {
        'annual_glab_capacity': annual_glab_capacity,
        'total_optical_modules': int(total_optical_modules),
        'monthly_optical_modules': int(monthly_optical_modules),
        'daily_optical_modules': int(daily_optical_modules),
        'production_feasible': production_feasible,
        'capacity_shortage': int(capacity_shortage),
        'optical_block_manufacturing_cost': int(optical_block_manufacturing_cost),
        'total_material_cost': int(total_material_cost),
        'total_labor_cost': int(total_labor_cost),
        'total_production_cost': int(total_production_cost),
        'annual_depreciation': int(annual_depreciation),
        'depreciation_cost': int(depreciation_cost),
        'annual_revenue': int(annual_revenue),
        'annual_production_cost': int(annual_production_cost),
        'annual_profit': int(annual_profit),
        'profit_margin': profit_margin
    }

if __name__ == "__main__":
    main()