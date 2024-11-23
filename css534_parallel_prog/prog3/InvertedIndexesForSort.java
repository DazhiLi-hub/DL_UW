import java.io.IOException;
import java.util.*;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;
import org.apache.hadoop.util.*;

public class InvertedIndexes {

    public static class Map extends MapReduceBase implements Mapper<LongWritable, Text, Text, Text> {
	// Get Job configuration for accessing parameters
	JobConf conf;
 	public void configure( JobConf job ) {
 		this.conf = job;
 	}
	
	public void map(LongWritable key, Text value, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
		// retrieve # keywords from JobConf
		int argc = Integer.parseInt( conf.get( "argc" ) );
		// parsing keyworods
		ArrayList<String> keywords = new ArrayList<String>();
		for (int i = 0; i < argc; i++) {
			keywords.add(conf.get("keyword" + i));
		}
		HashMap<String, Integer> docContainer = new HashMap<>();
		// get the current file name
		FileSplit fileSplit = ( FileSplit )reporter.getInputSplit( );
		String filename = "" + fileSplit.getPath( ).getName( );
	    String line = value.toString();
		// read v1, which is the context of every line
	    StringTokenizer tokenizer = new StringTokenizer(line);
		Text k2 = new Text();
		Text v2 = new Text();
	    while (tokenizer.hasMoreTokens()) {
			String currToken = tokenizer.nextToken();
			for (String keyword : keywords) {
				// matching with keyword, if matched, add to the next k,v pair
				if (currToken.equals(keyword)) {
					if (docContainer.containsKey(keyword+","+filename)) {
						Integer sum = docContainer.get(keyword+","+filename);
						sum += 1;
						docContainer.replace(keyword+","+filename, sum);
					} else {
						docContainer.put(keyword+","+filename, 1);
					}
				}
			}
	    }
		for (String keyFileName : docContainer.keySet()) {
			Integer occurTime = docContainer.get(keyFileName);
			String[] keyStr = keyFileName.split(",");
			k2.set(keyStr[0]);
			v2.set(keyStr[1] + " " +1);
			output.collect(k2, v2);
		}
	}
    }
	 
    public static class Reduce extends MapReduceBase implements Reducer<Text, Text, Text, Text> {
	public void reduce(Text key, Iterator<Text> values, OutputCollector<Text, Text> output, Reporter reporter) throws IOException {
		Text docListText = new Text();
		String singleLine = "";
	    while (values.hasNext()) {
			singleLine += values.next().toString() + " ";
	    }
		docListText.set(singleLine);
	    output.collect(key, docListText);
	}
    }
    
    public static void main(String[] args) throws Exception {
	// input format:
 	// hadoop jar invertedindexes.jar InvertedIndexes input output keyword1 keyword2 ...

	JobConf conf = new JobConf(InvertedIndexes.class);
	conf.setJobName("InvertedIndexes");

	conf.setInputFormat(TextInputFormat.class);
	conf.setOutputFormat(TextOutputFormat.class);
	FileInputFormat.setInputPaths(conf, new Path(args[0]));
	FileOutputFormat.setOutputPath(conf, new Path(args[1]));
	
	conf.setMapperClass(Map.class);
	conf.setMapOutputKeyClass(Text.class);
	conf.setMapOutputValueClass(Text.class);

	//conf.setCombinerClass(Reduce.class);

	conf.setReducerClass(Reduce.class);
	conf.setOutputKeyClass(Text.class);
	conf.setOutputValueClass(Text.class);

	conf.set( "argc", String.valueOf( args.length - 2 ) ); // argc maintains #keywords
 	for ( int i = 0; i < args.length - 2; i++ )
 		conf.set( "keyword" + i, args[i + 2] ); //keyword1, keyword2
	
	JobClient.runJob(conf);
    }
}
