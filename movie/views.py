from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import io
from collections import Counter
import urllib, base64
from .models import Movie
# Create your views here.

def home(request):
    #return HttpResponse('<h1>Welcome to Home page</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html',{'name':'Samuel Martínez'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies':movies})

def about(request):
    #return HttpResponse('<h1>Welcome to About page</h1>')
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email':email})


def _figure_to_base64(fig=None):
    """Convierte la figura activa (o la pasada) a base64 y la cierra."""
    if fig is None:
        fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img


def statistics_view(request):
    rows = Movie.objects.values('year', 'genre')

    year_counts = Counter()
    genre_counts = Counter()

    for r in rows:
        # ---- Conteo por año ----
        year = r['year'] if r['year'] else 'None'
        year_counts[year] += 1

        # ---- Conteo por género (SOLO el primero) ----
        raw = (r['genre'] or '').strip()
        first_genre = raw.split(',', 1)[0].strip() if raw else 'Unknown'
        genre_counts[first_genre] += 1

    # ---- Gráfica: Movies per year ----
    def parse_year(y):
        try:
            return int(y)
        except (TypeError, ValueError):
            return float('inf')  # "None" al final

    year_labels = sorted(year_counts.keys(), key=parse_year)
    year_values = [year_counts[k] for k in year_labels]

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    pos = range(len(year_labels))
    ax1.bar(pos, year_values, width=0.5, align='center')
    ax1.set_title('Movies per year')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of movies')
    ax1.set_xticks(list(pos))
    ax1.set_xticklabels(year_labels, rotation=90)
    fig1.subplots_adjust(bottom=0.3)
    graphic_year = _figure_to_base64(fig1)

    # ---- Gráfica: Movies per genre (primer género) ----
    genre_items = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    genre_labels = [k for k, _ in genre_items]
    genre_values = [v for _, v in genre_items]

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    pos = range(len(genre_labels))
    ax2.bar(pos, genre_values, width=0.5, align='center', color='red') 
    ax2.set_title('Movies per genre (first genre only)')
    ax2.set_xlabel('Genre')
    ax2.set_ylabel('Number of movies')
    ax2.set_xticks(list(pos))
    ax2.set_xticklabels(genre_labels, rotation=45, ha='right')
    fig2.subplots_adjust(bottom=0.3)
    graphic_genre = _figure_to_base64(fig2)

    return render(
        request,
        'statistics.html',
        {'graphic_year': graphic_year, 'graphic_genre': graphic_genre}
    )