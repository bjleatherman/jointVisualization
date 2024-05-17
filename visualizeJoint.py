import sqlite3
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
import math

now = datetime.datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))

# Path to the SQLite database file
db_folder_path = r'path to DB folder'
db_path = r'path to db'
db_full_path = db_folder_path + '\\' + db_path

# Set Joint No to visualize
  joint_no = 'joint_no'

# Set scale of Y Axis to make visualization easier
scale_for_diam = 2.5

# SQL query as a string variable
query = f'''SELECT * FROM FEATRS_VW
WHERE PIPE_JT_NUM = '{joint_no}' AND (FEATR_TP_NM = 'Metal Loss' OR FEATR_TP_NM = 'Metal Loss Group');'''

# Connect to the SQLite database
conn = sqlite3.connect(db_full_path)

# Execute the query and load the result into a pandas DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Get scale length
scale_x = round(df['JT_LEN'].iloc[0], 3)  # in meters
scale_y = df['NOMNL_PIPE_SZ'].iloc[0] * math.pi  # diam to circ in inches
scale_y = round(scale_y * 0.0254, 3) # convert to meters
print(f'{scale_x, scale_y}')

# ML points x-axis
x_axis_values = df['DSTNC_FM_USTREM_WELD']

# ML points y-axis
df['CLCK'] = df['ORNTN'].str[11:16]
df['HOURS'] = df['CLCK'].str[:2].astype(int)
df['MINUTES'] = df['CLCK'].str[3:5].astype(int)
df['DEGREES'] = (df['HOURS'] * 30) + (df['MINUTES'] * 0.5)
# Normalize degrees using scale_y which has been converted to meters
df['NRMLZD_Y'] = (df['DEGREES'] / 360) * scale_y
df['FLIPPED_Y'] = scale_y - df['NRMLZD_Y']
df['SCALED_Y'] = df['FLIPPED_Y'] * scale_for_diam

# Force aspect ratio
adjusted_scale_y = scale_y * scale_for_diam
aspect_ratio = scale_x / (adjusted_scale_y)

fig, ax = plt.subplots()
ax.scatter(x_axis_values, df['SCALED_Y'])
ax.set_xlabel('Distance from U/S Weld [m]')
ax.set_ylabel(f'Orientation (scale factor:{scale_for_diam})')
# ax.set_ylabel(f'Normalized Y-axis (Degrees / NOMNL_PIPE_SZ in meters)* scale factor({scale_for_diam})')
ax.set_title(f'View of Joint {joint_no} in {db_path}')

print(aspect_ratio)


# Set aspect ratio to be equal
ax.set_aspect('equal', adjustable='box')

# Set the limits based on the real-world dimensions
# Making sure the limits take into account the aspect ratio
x_margin = (adjusted_scale_y * aspect_ratio - scale_x) / 2 if aspect_ratio > 1 else 0
y_margin = (scale_x / aspect_ratio - adjusted_scale_y) / 2 if aspect_ratio < 1 else 0

ax.set_xlim(0 - x_margin, scale_x + x_margin)
ax.set_ylim(0 - y_margin, adjusted_scale_y + y_margin)

plt.show()

now = datetime.datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))
