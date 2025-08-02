import psycopg2
import time
import csv
from typing import List, Tuple, Optional
import os
from dotenv import load_dotenv
from prettytable import PrettyTable

load_dotenv()

class CustomerPurchasesDBSearchAnalyzer:
    def __init__(self):
        """Initialize the search performance analyzer"""
        self.connection_params = self.load_db_config()
        self.connection = None
        self.product_data = []
        self.connect_to_database()
        
    def load_db_config(self) -> dict:
        """Load database configuration from environment variables"""
        db_connection = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # Validate required configuration
        missing_config = []
        for key, value in db_connection.items():
            if not value:
                missing_config.append(key.upper())

        if missing_config:
            print(f"❌ WARNING: Missing configuration: {', '.join(missing_config)}")
            print(f"Please check your .env file")
        else:
            print("✓ Database configuration loaded successfully")
        
        return db_connection
        
    def connect_to_database(self):
        """Connect to PostgreSQL database server"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            print("✓ Successfully connected to PostgreSQL database")
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            print("\nTrying alternative: Loading from CSV file...")
            self.load_from_csv()
    
    # def load_from_csv(self):
    #     """Fallback: Load data from CSV if database connection fails"""
    #     try:
    #         csv_file = os.getenv('CSV_FILE', 'purchases_data.csv')
    #         with open(csv_file, 'r', encoding='utf-8') as file:
    #             csv_reader = csv.DictReader(file)
    #             self.product_data = list(csv_reader)
    #         print(f"✓ Loaded {len(self.product_data)} records from {csv_file}")
    #     except Exception as e:
    #         print(f"✗ Error loading CSV: {e}")
    
    def fetch_all_data(self) -> List[dict]:
        """Fetch all data from the database"""
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT customer_id, customer_name, purchase_date, 
                           product_id, product_category, amount
                    FROM customer_purchases
                    ORDER BY customer_id
                """)
                
                columns = [desc[0] for desc in cursor.description] # Get column names
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                self.product_data = [dict(zip(columns, row)) for row in rows] # List of dictionaries  with column names as keys and row values as values (per row/record)
                # print(self.product_data)
                cursor.close()
                
                print(f"✓ Fetched {len(self.product_data)} records from database")
                return self.product_data
                
            except Exception as e:
                print(f"❌ Error fetching data: {e}")
                return []
        else:
            return self.product_data if self.product_data else []
    
    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a specific column"""
        if not self.product_data:
            return []
        
        unique_values = list(set(str(record[column]) for record in self.product_data))
        return sorted(unique_values)
    
    def display_available_data(self):
        """Display what data is available for searching in tabular format"""
        print("\n" + "="*100)
        print("AVAILABLE DATA FOR SEARCHING")
        print("="*100)
        
        if not self.product_data:
            print("No data available")
            return
        
        print(f"Total Records: {len(self.product_data)}")
        
        # Display data in tabular format using PrettyTable
        print("\nDATA PREVIEW:")
        
        data_table = PrettyTable() # Create table for data preview
        headers = list(self.product_data[0].keys()) # Get headers from first record/row
        data_table.field_names = [header.replace('_', ' ').title() for header in headers] # Format headers
        
        display_limit = len(self.product_data)
        for i in range(display_limit):
            row = []
            for header in headers:
                value = str(self.product_data[i][header]) # Get value for each header and convert to string
                # Truncate very long values
                if len(value) > 20:
                    value = value[:17] + "..."
                row.append(value)
            data_table.add_row(row)
        
        print(data_table)
        
        
        # Indexed and unindexed columns information
        columns_info = {
            'customer_id': {'indexed': True, 'description': 'Primary Key - Very Fast'},
            'product_category': {'indexed': True, 'description': 'Secondary Index - Fast'},
            'purchase_date': {'indexed': True, 'description': 'Secondary Index - Fast'},
            'product_id': {'indexed': False, 'description': 'No Index - Slower'},
            'customer_name': {'indexed': False, 'description': 'No Index - Slower'},
            'amount': {'indexed': False, 'description': 'No Index - Slower'}
        }
        
        print("\n" + "="*100)
        print("COLUMN INFORMATION AND INDEX STATUS:")
        print("="*100)
        
        # Create table for column information
        column_table = PrettyTable()
        column_table.field_names = ["Column", "Index Status", "Unique Values", "Description"]
        
        for column, info in columns_info.items():
            if column in self.product_data[0]:
                unique_values = self.get_unique_values(column) # Get unique values for the column
                status = "INDEXED" if info['indexed'] else "UNINDEXED"
                column_table.add_row([
                    column.replace('_', ' ').title(),
                    status,
                    len(unique_values),
                    info['description']
                ])
        
        print(column_table)
        
    
    def database_search_indexed(self, search_value: str, column: str) -> Tuple[Optional[dict], float]:
        """Search database using an indexed column"""
        if not self.connection:
            print("No database connection available")
            return None, 0
        
        start_time = time.perf_counter()
        
        try:
            cursor = self.connection.cursor()
            query = f"SELECT * FROM customer_purchases WHERE {column} = %s"
            cursor.execute(query, (search_value,))
            result = cursor.fetchone()
            
            end_time = time.perf_counter()
            query_time = end_time - start_time
            cursor.close()
            
            if result:
                columns = ['customer_id', 'customer_name', 'purchase_date', 'product_id', 'product_category', 'amount']
                result_dict = dict(zip(columns, result))
                print(f"  Database query (with INDEX): {query_time:.6f} seconds")
                return result_dict, query_time
            else:
                print(f"  Database query (with INDEX): Not found in {query_time:.6f} seconds")
                return None, query_time
                
        except Exception as e:
            print(f"Database query error: {e}")
            return None, 0
    
    def database_search_unindexed(self, search_value: str, column: str) -> Tuple[Optional[dict], float]:
        """Search database using an unindexed column (full table scan)"""
        if not self.connection:
            print("No database connection available")
            return None, 0
        
        start_time = time.perf_counter()
        
        try:
            cursor = self.connection.cursor()
            query = f"SELECT * FROM customer_purchases WHERE {column} = %s"
            cursor.execute(query, (search_value,))
            result = cursor.fetchone()
            
            end_time = time.perf_counter()
            query_time = end_time - start_time
            cursor.close()
            
            if result:
                columns = ['customer_id', 'customer_name', 'purchase_date', 'product_id', 'product_category', 'amount']
                result_dict = dict(zip(columns, result))
                print(f"  Database query (WITHOUT INDEX): {query_time:.6f} seconds")
                return result_dict, query_time
            else:
                print(f"  Database query (WITHOUT INDEX): Not found in {query_time:.6f} seconds")
                return None, query_time
                
        except Exception as e:
            print(f"Database query error: {e}")
            return None, 0
    
    def binary_search(self, target_value: str, search_column: str) -> Tuple[Optional[dict], int]:
        """Implement binary search algorithm (simulates indexed search)"""
        try:
            sorted_data = sorted(self.product_data, key=lambda x: str(x[search_column]))
        except KeyError:
            print(f"Column '{search_column}' not found in data")
            return None, 0
        
        left, right = 0, len(sorted_data) - 1
        comparisons = 0
        
        print(f"  Binary Search: Searching sorted data...")
        
        while left <= right:
            comparisons += 1
            mid = (left + right) // 2
            mid_value = str(sorted_data[mid][search_column])
            
            if mid_value == str(target_value):
                print(f"  Binary Search: Found after {comparisons} comparisons")
                return sorted_data[mid], comparisons
            elif mid_value < str(target_value):
                left = mid + 1
            else:
                right = mid - 1
        
        print(f"  Binary Search: Not found after {comparisons} comparisons")
        return None, comparisons
    
    def sequential_search(self, target_value: str, search_column: str) -> Tuple[Optional[dict], int]:
        """Implement sequential search algorithm (simulates unindexed search)"""
        comparisons = 0
        
        print(f"  Sequential Search: Searching unsorted data...")
        
        for record in self.product_data:
            comparisons += 1
            if str(record[search_column]) == str(target_value):
                print(f"  Sequential Search: Found after {comparisons} comparisons")
                return record, comparisons
        
        print(f"  Sequential Search: Not found after {comparisons} comparisons")
        return None, comparisons
    
    def perform_search_comparison(self, search_value: str, column: str):
        """Perform and display comprehensive search comparison"""
        print(f"\nSEARCHING FOR: {column} = '{search_value}'")
        print("=" * 60)
        
        # Determine if column is indexed
        indexed_columns = ['customer_id', 'product_category', 'purchase_date']
        is_indexed = column in indexed_columns
        
        print(f"Column '{column}' is {'INDEXED' if is_indexed else 'NOT INDEXED'}")
        
        # Database searches
        if is_indexed:
            db_result, db_time = self.database_search_indexed(search_value, column)
        else:
            db_result, db_time = self.database_search_unindexed(search_value, column)
        
        # Algorithm comparisons
        binary_result, binary_comparisons = self.binary_search(search_value, column)
        sequential_result, sequential_comparisons = self.sequential_search(search_value, column)
        
        # Performance summary
        print(f"\nPERFORMANCE COMPARISON:")
        print(f"  Database Query Time: {db_time:.6f} seconds")
        print(f"  Binary Search:       {binary_comparisons} comparisons")
        print(f"  Sequential Search:   {sequential_comparisons} comparisons")
        
        if sequential_comparisons > 0 and binary_comparisons > 0:
            speedup = sequential_comparisons / binary_comparisons
            print(f"  Binary search is {speedup:.1f}x faster than sequential search")
        
        # Display found record
        if db_result:
            print(f"\nFOUND RECORD:")
            for key, value in db_result.items():
                print(f"  {key}: {value}")
        else:
            print(f"\nNo record found with {column} = '{search_value}'")
    
    def interactive_menu(self):
        """Display interactive menu for user choices"""
        while True:
            print("\n" + "="*70)
            print("DATABASE SEARCH PERFORMANCE ANALYZER")
            print("="*70)
            print("1. Search by Customer ID (INDEXED)")
            print("2. Search by Product ID (UNINDEXED)")
            print("3. Search by Product Category (INDEXED)")
            print("4. Search by Customer Name (UNINDEXED)")
            print("5. Search by Purchase Date (INDEXED)")
            print("6. Search by Amount (UNINDEXED)")
            print("7. View Available Data")
            print("8. Run Performance Tests")
            print("0. Exit")
            
            choice = input("\nSelect an option (0-9): ").strip()
            
            if choice == '0':
                print("Thank you for using the Search Performance Analyzer!")
                break
            elif choice == '1':
                self.search_by_column('customer_id', 'Customer ID')
            elif choice == '2':
                self.search_by_column('product_id', 'Product ID')
            elif choice == '3':
                self.search_by_column('product_category', 'Product Category')
            elif choice == '4':
                self.search_by_column('customer_name', 'Customer Name')
            elif choice == '5':
                self.search_by_column('purchase_date', 'Purchase Date')
            elif choice == '6':
                self.search_by_column('amount', 'Amount')
            elif choice == '7':
                self.display_available_data()
            elif choice == '8':
                self.run_performance_tests()
            else:
                print("Invalid choice. Please select 0-9.")
            
            input("\nPress Enter to continue...")
    
    def search_by_column(self, column: str, display_name: str):
        """Generic search function for any column"""
        print(f"\n{display_name.upper()} SEARCH")
        available_values = self.get_unique_values(column)
        
        print(f"Available {display_name}s: {', '.join(available_values[:10])}")
        if len(available_values) > 10:
            print(f"... and {len(available_values)-10} more")
        
        search_value = input(f"\nEnter {display_name} to search: ").strip()
        if search_value:
            self.perform_search_comparison(search_value, column)
    
    def run_performance_tests(self):
        """Run automated performance tests"""
        print("\nRUNNING PERFORMANCE TESTS")
        print("="*50)
        
        if not self.product_data:
            print("No data available for testing")
            return
        
        # Test with first record's data
        test_cases = [
            {'column': 'customer_id', 'value': self.product_data[0]['customer_id'], 'indexed': True},
            {'column': 'product_id', 'value': self.product_data[0]['product_id'], 'indexed': False},
            {'column': 'product_category', 'value': self.product_data[0]['product_category'], 'indexed': True},
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest {i}/3: {test['column']} ({'INDEXED' if test['indexed'] else 'UNINDEXED'})")
            self.perform_search_comparison(test['value'], test['column'])
    

    
    def display_index_information(self):
        """Display information about database indexes"""
        if not self.connection:
            print("No database connection available")
            return None, 0
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'customer_purchases'
                ORDER BY indexname
            """)
            
            indexes = cursor.fetchall()
            cursor.close()
            
            print("\nDATABASE INDEX INFORMATION")
            print("="*50)
            
            for index_name, index_def in indexes:
                print(f"\n{index_name}:")
                print(f"   {index_def}")
            
        except Exception as e:
            print(f"Error fetching index information: {e}")
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

def main():
    """Main function to run the search performance analyzer"""
    print("DATABASE SEARCH PERFORMANCE ANALYZER")
    print("="*70)
    print("This tool demonstrates the performance difference between")
    print("indexed and unindexed database searches.")
    print("="*70)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\nNo .env file found - Running in DEMO MODE")
        print("To connect to your database, create a .env file with:")
        print("   DB_HOST=localhost")
        print("   DB_NAME=your_database")
        print("   DB_USER=your_username")
        print("   DB_PASSWORD=your_password")
        print("   DB_PORT=5432")
    
    # Initialize search system
    analyzer = CustomerPurchasesDBSearchAnalyzer()
    
    # Fetch data
    data = analyzer.fetch_all_data()
    
    if not data:
        print("No data available - cannot proceed")
        return
    
    # Display index information
    analyzer.display_index_information()
    
    try:
        # Start interactive menu
        analyzer.interactive_menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    finally:
        # Clean up
        analyzer.close_connection()
        print("Thank you for learning about database performance!")

if __name__ == "__main__":
    main()