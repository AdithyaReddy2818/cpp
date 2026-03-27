"""
Architecture diagram generator for the Neighbourhood Safety Incident Reporting App.
Produces a PNG diagram showing the system architecture using matplotlib.
Author: Adithya Reddy Madireddy
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def create_architecture_diagram():
    """Generate and save the system architecture diagram as a PNG file."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')

    # Title
    ax.text(8, 9.5, 'Neighbourhood Safety Incident Reporting App',
            ha='center', va='center', fontsize=16, fontweight='bold', color='#1e3a5f')
    ax.text(8, 9.1, 'System Architecture - Adithya Reddy Madireddy',
            ha='center', va='center', fontsize=10, color='#636e72')

    # Frontend box
    frontend = mpatches.FancyBboxPatch((0.5, 6.5), 3.5, 2.0,
                                        boxstyle="round,pad=0.15", facecolor='#3498db',
                                        edgecolor='#2980b9', linewidth=2)
    ax.add_patch(frontend)
    ax.text(2.25, 7.8, 'React Frontend', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(2.25, 7.3, 'Dashboard | Incidents\nUsers | Map | Reports',
            ha='center', va='center', fontsize=8, color='#ecf0f1')
    ax.text(2.25, 6.8, 'Port 3002', ha='center', va='center',
            fontsize=7, color='#bdc3c7')

    # Backend box
    backend = mpatches.FancyBboxPatch((6, 6.5), 4, 2.0,
                                       boxstyle="round,pad=0.15", facecolor='#27ae60',
                                       edgecolor='#219a52', linewidth=2)
    ax.add_patch(backend)
    ax.text(8, 7.8, 'Flask Backend API', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(8, 7.3, 'Routes | Models | Services\nFlask-SQLAlchemy | Flask-CORS',
            ha='center', va='center', fontsize=8, color='#ecf0f1')
    ax.text(8, 6.8, 'Port 5002', ha='center', va='center',
            fontsize=7, color='#bdc3c7')

    # SafeZone Library box
    safezone = mpatches.FancyBboxPatch((12, 6.5), 3.5, 2.0,
                                        boxstyle="round,pad=0.15", facecolor='#8e44ad',
                                        edgecolor='#7d3c98', linewidth=2)
    ax.add_patch(safezone)
    ax.text(13.75, 7.8, 'SafeZone Library', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(13.75, 7.3, 'IncidentClassifier | ZoneManager\nAlertEngine | TrendAnalyzer',
            ha='center', va='center', fontsize=8, color='#ecf0f1')
    ax.text(13.75, 6.8, 'ReportGenerator', ha='center', va='center',
            fontsize=7, color='#bdc3c7')

    # Database box
    db = mpatches.FancyBboxPatch((1.5, 4.0), 2.5, 1.5,
                                  boxstyle="round,pad=0.15", facecolor='#e67e22',
                                  edgecolor='#d35400', linewidth=2)
    ax.add_patch(db)
    ax.text(2.75, 5.0, 'SQLite / DynamoDB', ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')
    ax.text(2.75, 4.5, 'Incidents | Users\nComments | Zones',
            ha='center', va='center', fontsize=7, color='#fdf2e9')

    # AWS Services
    aws_services = [
        ('DynamoDB', '#2c3e50', 0.5, 1.5),
        ('S3', '#2c3e50', 3.2, 1.5),
        ('SNS', '#2c3e50', 5.9, 1.5),
        ('Location Svc', '#2c3e50', 8.6, 1.5),
        ('SES', '#2c3e50', 11.3, 1.5),
        ('Lambda', '#2c3e50', 14.0, 1.5),
    ]

    for name, color, x, y in aws_services:
        svc = mpatches.FancyBboxPatch((x, y), 2.2, 1.2,
                                       boxstyle="round,pad=0.1", facecolor='#f39c12',
                                       edgecolor='#e67e22', linewidth=1.5)
        ax.add_patch(svc)
        ax.text(x + 1.1, y + 0.7, name, ha='center', va='center',
                fontsize=8, fontweight='bold', color='#2c3e50')
        ax.text(x + 1.1, y + 0.3, 'AWS', ha='center', va='center',
                fontsize=7, color='#7f8c8d')

    # Arrows: Frontend -> Backend
    ax.annotate('', xy=(6, 7.5), xytext=(4, 7.5),
                arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))
    ax.text(5, 7.7, 'REST API', ha='center', fontsize=7, color='#2c3e50')

    # Backend -> SafeZone
    ax.annotate('', xy=(12, 7.5), xytext=(10, 7.5),
                arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))
    ax.text(11, 7.7, 'Import', ha='center', fontsize=7, color='#2c3e50')

    # Backend -> Database
    ax.annotate('', xy=(2.75, 5.5), xytext=(7.5, 6.5),
                arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.5))

    # Backend -> AWS Services
    for i, (name, _, x, y) in enumerate(aws_services):
        ax.annotate('', xy=(x + 1.1, 2.7), xytext=(8, 6.5),
                    arrowprops=dict(arrowstyle='->', color='#e67e22', lw=1, alpha=0.6))

    # AWS Cloud boundary
    cloud = mpatches.FancyBboxPatch((0.2, 1.2), 15.6, 1.8,
                                     boxstyle="round,pad=0.2", facecolor='none',
                                     edgecolor='#e67e22', linewidth=2, linestyle='dashed')
    ax.add_patch(cloud)
    ax.text(8, 0.8, 'AWS Cloud Services (Mock Mode by Default)',
            ha='center', va='center', fontsize=9, color='#e67e22', fontstyle='italic')

    plt.tight_layout()
    plt.savefig('architecture_diagram.png', dpi=150, bbox_inches='tight',
                facecolor='#f8f9fa', edgecolor='none')
    print("Architecture diagram saved as architecture_diagram.png")


if __name__ == '__main__':
    create_architecture_diagram()
