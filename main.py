from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, LotteryResult
import json
import os
from utils import get_all_next_draws

app = FastAPI(title="Lotto Data Provider")

# Templates
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, type: str = None, db: Session = Depends(get_db)):
    # Get latest results for each type or filtered type
    all_types = ["ไทย", "ลาวพัฒนา", "ฮานอย", "ฮานอยพิเศษ"]
    display_types = [type] if type and type in all_types else all_types
    
    latest_results = []
    for t in display_types:
        res = db.query(LotteryResult).filter(LotteryResult.type == t).order_by(LotteryResult.draw_date.desc()).first()
        if res:
            latest_results.append(res)
    
    threshold_mins = int(os.getenv("COUNTDOWN_THRESHOLD_MINUTES", "1440"))
    next_draws = get_all_next_draws(threshold_mins)
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "results": latest_results, 
            "next_draws": next_draws, 
            "current_type": type,
            "all_types": all_types
        }
    )

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, type: str = None, db: Session = Depends(get_db)):
    # Get filtered results for history page
    query = db.query(LotteryResult)
    if type:
        query = query.filter(LotteryResult.type == type)
    
    results = query.order_by(LotteryResult.draw_date.desc()).limit(100).all()
    all_types = ["ไทย", "ลาวพัฒนา", "ฮานอย", "ฮานอยพิเศษ"]
    
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "results": results, 
            "current_type": type,
            "all_types": all_types
        }
    )

@app.get("/api/lottery/latest")
async def get_latest(db: Session = Depends(get_db)):
    types = ["ไทย", "ลาวพัฒนา", "ฮานอย", "ฮานอยพิเศษ"]
    results = {}
    for t in types:
        res = db.query(LotteryResult).filter(LotteryResult.type == t).order_by(LotteryResult.draw_date.desc()).first()
        if res:
            results[t] = {
                "sanook_id": res.sanook_id,
                "draw_title": res.draw_title,
                "draw_date": res.draw_date.isoformat(),
                "prizes": res.prizes,
                "url": res.url
            }
    return results

@app.get("/api/lottery/list")
async def list_lottery(type: str = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(LotteryResult)
    if type:
        query = query.filter(LotteryResult.type == type)
    
    results = query.order_by(LotteryResult.draw_date.desc()).limit(limit).all()
    return [{
        "sanook_id": r.sanook_id,
        "type": r.type,
        "draw_title": r.draw_title,
        "draw_date": r.draw_date.isoformat(),
        "prizes": r.prizes,
        "url": r.url
    } for r in results]

@app.get("/api/lottery/next_draws")
async def get_next_draws_api():
    threshold_mins = int(os.getenv("COUNTDOWN_THRESHOLD_MINUTES", "1440"))
    return get_all_next_draws(threshold_mins)

@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request, db: Session = Depends(get_db)):
    # Calculate stats from latest 100 results
    results = db.query(LotteryResult).order_by(LotteryResult.draw_date.desc()).limit(100).all()
    
    # Simple frequency analysis for 2-digit prizes
    two_digit_freq = {}
    for r in results:
        num = r.prizes.get("เลขท้าย_2_ตัว")
        if num and num.isdigit():
            two_digit_freq[num] = two_digit_freq.get(num, 0) + 1
            
    # Sort and take top 5
    hot_numbers = sorted(two_digit_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return templates.TemplateResponse(
        request=request,
        name="statistics.html",
        context={"results": results, "hot_numbers": hot_numbers}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
